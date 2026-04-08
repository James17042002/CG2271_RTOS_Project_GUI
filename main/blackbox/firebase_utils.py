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
