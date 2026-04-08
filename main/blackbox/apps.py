from django.apps import AppConfig


class BlackboxConfig(AppConfig):
    name = "blackbox"

    def ready(self):
        """
        Runs once when the Django project starts.
        Syncs the Active_Run status to Firebase on boot.
        """
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
