from .models import Run

def active_run_status(request):
    """
    Returns the status of whether there is an active recording session.
    Used to toggle the navbar 'Start a Run' button text and color.
    """
    return {
        'has_active_run': Run.objects.filter(is_active=True).exists()
    }
