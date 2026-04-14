import firebase_admin
from firebase_admin import credentials, db
from django.conf import settings

def init_firebase():
    """
    Initializes the Firebase Admin SDK using settings.
    Idempotent: safe to call multiple times.
    """
    if not firebase_admin._apps:
        cred = credentials.Certificate(str(settings.FIREBASE_CREDENTIALS_PATH))
        firebase_admin.initialize_app(cred, {
            'databaseURL': settings.FIREBASE_DATABASE_URL
        })

def sync_active_run_status():
    """
    Checks the local Django database for any active runs and
    synchronizes the 'Active_Run' boolean in Firebase.
    """
    from .models import Run  # Import inside to avoid circular dependencies
    
    init_firebase()
    
    # Check if ANY run is currently active
    has_active_run = Run.objects.filter(is_active=True).exists()
    
    # Update the Firebase root variable
    db.reference('Active_Run').set(has_active_run)
    
    return has_active_run

def sync_run_config(run):
    """
    Synchronizes the thresholds of a specific run to the 'run_config' node in Firebase.
    """
    init_firebase()
    
    config_data = {
        'temp_threshold': run.temp_threshold,
        'humidity_threshold': run.humidity_threshold,
        'light_threshold': run.light_threshold,
    }
    
    # Update the Firebase run_config node
    db.reference('run_config').set(config_data)
    
    return config_data
