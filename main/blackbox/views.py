from django.db.models import Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.generic import TemplateView
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView
from .models import Run, SensorReading
from .tables import RunTable
from .filters import RunFilter
import json


class HomeView(TemplateView):
    template_name = "blackbox/home.html"


class RunListView(SingleTableMixin, FilterView):
    model = Run
    table_class = RunTable
    template_name = "blackbox/run_list.html"
    filterset_class = RunFilter
    context_object_name = "runs"
    paginate_by = 10


def run_detail(request, pk):
    """
    Renders detailed analytics for a single run, including averages and graphs.
    """
    run = get_object_or_404(Run, pk=pk)
    readings = SensorReading.objects.filter(run=run).order_by("timestamp")
    
    # Calculate Averages
    from django.db.models import Count, Q
    last_reading = readings.last()
    stats = readings.aggregate(
        avg_temp=Avg("temperature"),
        avg_hum=Avg("humidity"),
        avg_light=Avg("light_level"),
    )
    stats['temp_violations'] = last_reading.temp_exceeded if last_reading else 0
    stats['hum_violations'] = last_reading.humi_exceeded if last_reading else 0
    stats['light_violations'] = last_reading.light_exceeded if last_reading else 0
    
    # Prepare data for Chart.js and Leaflet
    chart_data = {
        "labels": [timezone.localtime(r.timestamp).strftime("%H:%M:%S") if r.timestamp else "N/A" for r in readings],
        "temp": [r.temperature for r in readings],
        "hum": [r.humidity for r in readings],
        "light": [r.light_level for r in readings],
        "lats": [r.latitude for r in readings],
        "lngs": [r.longitude for r in readings],
    }
    
    return render(request, "blackbox/run_detail.html", {
        "run": run,
        "stats": stats,
        "chart_data_json": json.dumps(chart_data)
    })


def start_run_page(request):
    """
    Renders the Start Run page with the current active run (if any).
    """
    active_run = Run.objects.filter(is_active=True).first()
    return render(request, "blackbox/start_run.html", {"active_run": active_run})


from .firebase_utils import sync_active_run_status, sync_run_config


def toggle_run(request):
    """
    Starts a new run (if none is active) or stops the current one.
    Also syncs the 'Active_Run' status to Firebase.
    """
    if request.method == "POST":
        active_run = Run.objects.filter(is_active=True).first()
        
        if active_run:
            # Stop the run
            active_run.is_active = False
            active_run.ended_at = timezone.now()
            active_run.save()
        else:
            # Start a new run
            object_name = request.POST.get("object_name", "Unnamed Run")
            
            # Extract thresholds with defaults
            temp_threshold = request.POST.get("temp_threshold")
            humidity_threshold = request.POST.get("humidity_threshold")
            light_threshold = request.POST.get("light_threshold")
            
            temp_threshold = float(temp_threshold) if temp_threshold else 50.0
            humidity_threshold = float(humidity_threshold) if humidity_threshold else 90.0
            light_threshold = float(light_threshold) if light_threshold else 3000.0
            
            new_run = Run.objects.create(
                object=object_name, 
                is_active=True,
                temp_threshold=temp_threshold,
                humidity_threshold=humidity_threshold,
                light_threshold=light_threshold
            )
            
            # Sync the run configuration to Firebase
            sync_run_config(new_run)
        
        # Sync the global 'Active_Run' status to Firebase
        sync_active_run_status()
            
    return redirect("start_run_page")


def live_readings(request):
    active_run = Run.objects.filter(is_active=True).first()
    readings = []
    if active_run:
        active_run.refresh_from_db()  # Get latest counter values
        readings = SensorReading.objects.filter(run=active_run).order_by("-timestamp")[:10]
    
    return render(request, "blackbox/partials/readings_table.html", {
        "readings": readings,
        "active_run": active_run
    })

def live_run_status(request):
    active_run = Run.objects.filter(is_active=True).first()
    if active_run:
        active_run.refresh_from_db()
    return render(request, "blackbox/partials/run_status.html", {"active_run": active_run})
