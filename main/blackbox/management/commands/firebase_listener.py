"""
Custom Django management command: firebase_listener
----------------------------------------------------
Run with:   python manage.py firebase_listener
Keeps a persistent WebSocket open to Firebase Realtime Database and saves
every telemetry packet the ESP32 pushes into the local SQLite database.
"""

import time
import django
import firebase_admin
from firebase_admin import credentials, db
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Starts a persistent listener to sync Firebase telemetry -> Django SQL"

    # --- Firebase initialisation ----------------------------------------------

    def _init_firebase(self):
        """Initialise the Firebase Admin SDK (idempotent - safe to call once)."""
        if not firebase_admin._apps:
            cred = credentials.Certificate(str(settings.FIREBASE_CREDENTIALS_PATH))
            firebase_admin.initialize_app(cred, {
                "databaseURL": settings.FIREBASE_DATABASE_URL,
            })
            self.stdout.write(self.style.SUCCESS("Firebase Admin SDK initialised."))
        else:
            self.stdout.write("Firebase app already initialised - reusing existing connection.")

    # --- Callback -------------------------------------------------------------

    def _make_callback(self):
        """
        Returns a closure so the callback can call self.stdout without
        capturing 'self' at module level (keeps the code testable).
        """
        # Import here to avoid issues before Django setup is complete
        from blackbox.models import Run, SensorReading  # noqa: PLC0415

        def listener_callback(event):
            """
            Fires automatically whenever the ESP32 updates the
            Firebase node we are listening to.

            event.data  -> the new JSON value at that node
            event.event_type -> 'put' | 'patch' | 'cancel'
            event.path  -> relative path within the node
            """
            if not event.data:
                self.stdout.write(self.style.WARNING("Empty event received - skipping."))
                return

            data = event.data  # dict sent by the ESP32

            # Fetch the most recently created Run (Optional)
            active_run = Run.objects.filter(is_active=True).first()

            def save_reading(payload, run_obj, firebase_key):
                """Helper to create a SensorReading from a JSON payload."""
                if not isinstance(payload, dict):
                    return None

                from django.utils import timezone
                import datetime

                # Firebase provides timestamp in milliseconds (e.g. 1775577849612)
                ts_ms = payload.get("ts")
                if ts_ms:
                    # Convert to seconds and create an aware datetime
                    dt = datetime.datetime.fromtimestamp(ts_ms / 1000.0, tz=datetime.timezone.utc)
                else:
                    dt = timezone.now()

                reading, created = SensorReading.objects.get_or_create(
                    firebase_id=firebase_key,
                    defaults={
                        "run": run_obj,
                        "timestamp": dt,
                        "event_status": payload.get("event_status", ""),
                        "temperature": payload.get("temperature", 0.0),
                        "humidity": payload.get("humidity", 0.0),
                        "light_level": payload.get("light_level", 0.0),
                        "latitude": payload.get("latitude", 0.0),
                        "longitude": payload.get("longitude", 0.0),
                    }
                )
                
                if not created:
                    return None
                    
                return reading

            # The 'event.data' can be a single reading OR a dictionary of multiple readings
            # (especially on the first connection if historical data exists).
            if isinstance(event.data, dict):
                # Check if it looks like a single reading (has a 'temperature' key)
                # or a collection of readings (keys are Firebase push IDs)
                if "temperature" in event.data:
                    # Single reading: the Firebase push ID is in event.path (e.g. "/-OpccXYZ...")
                    push_id = event.path.strip("/")
                    if not push_id:
                        # Fallback if path is unexpectedly root
                        import time
                        push_id = f"unknown_{int(time.time() * 1000)}"
                    readings = {push_id: event.data}
                else:
                    # Collection of readings
                    readings = event.data
            else:
                self.stdout.write(self.style.WARNING(f"Received non-dictionary data: {event.data}"))
                return

            for key, payload in readings.items():
                reading = save_reading(payload, active_run, key)
                if reading:
                    self.stdout.write(
                        f"Saved Reading #{reading.id} (Key: {key}) - "
                        f"Status: {reading.event_status} | "
                        f"Temp={reading.temperature}C  "
                        f"GPS=({reading.latitude}, {reading.longitude}) "
                        f"-> Run: {active_run.id if active_run else 'None'}"
                    )

        return listener_callback

    # --- Entry point ----------------------------------------------------------

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            "Firebase Listener starting...\n"
            "   Press Ctrl+C to stop.\n"
        ))

        # 1. Boot Firebase
        self._init_firebase()

        # 2. Attach the listener to the node where ESP32 shipment logs are stored.
        firebase_path = "/shipment_logs"
        self.stdout.write(f"Listening on Firebase path: {firebase_path}")
        db.reference(firebase_path).listen(self._make_callback())

        # 3. Block forever (the .listen() callback runs in a background thread)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.ERROR("\nListener stopped by user."))
