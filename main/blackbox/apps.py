import os
import sys
import threading
from django.apps import AppConfig


class BlackboxConfig(AppConfig):
    name = "blackbox"

    def ready(self):
        # Avoid running twice (autoreload spawns two processes)
        if os.environ.get("RUN_MAIN") == "true" or "gunicorn" in sys.modules:
            from .firebase_utils import sync_active_run_status

            try:
                sync_active_run_status()
                print("Firebase Active_Run status synced on startup.")
            except Exception as e:
                print(f"Warning: Failed to sync Firebase on startup: {e}")

            # Start firebase_listener in a background thread
            from django.core.management import call_command

            thread = threading.Thread(
                target=call_command,
                args=("firebase_listener",),
                daemon=True,
            )
            thread.start()
            print("Firebase listener started in background thread.")
"""
from django.apps import AppConfig


class BlackboxConfig(AppConfig):
    name = "blackbox"

    def ready(self):
        import os
        import sys

        # Avoid running during management commands (migrations, etc.)
        if 'runserver' in sys.argv:
            from .firebase_utils import sync_active_run_status
            try:
                sync_active_run_status()
                print("Firebase Active_Run status synced on startup.")
            except Exception as e:
                print(f"Warning: Failed to sync Firebase on startup: {e}")
"""