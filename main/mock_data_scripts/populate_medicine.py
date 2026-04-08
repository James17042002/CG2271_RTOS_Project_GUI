import os
import django
import random
from datetime import timedelta
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from blackbox.models import Run, SensorReading

def populate():
    print("Populating 'medicine' run with dummy data...")
    
    # 1. Create or get the 'medicine' run
    run, created = Run.objects.get_or_create(object="medicine")
    if not created:
        # Clear existing readings if the run already existed to start fresh
        run.readings.all().delete()
        print(f"Cleared existing data for Run #{run.id}")
    
    run.is_active = False
    run.save()

    # 2. Generate dummy readings
    start_time = timezone.now() - timedelta(hours=2)
    # Starting coordinates (NUS, Singapore)
    lat, lng = 1.2966, 103.7764
    
    readings = []
    for i in range(25):
        timestamp = start_time + timedelta(minutes=i * 5)
        
        # Realistic medicine cooling range (2-8 C)
        temp = round(random.uniform(3.5, 6.5), 1)
        hum = round(random.uniform(48.0, 52.0), 1)
        light = round(random.uniform(150, 250), 0)
        
        # Simulate movement (approx 0.001 deg per step)
        lat += random.uniform(0.0001, 0.0005)
        lng += random.uniform(0.0001, 0.0005)
        
        reading = SensorReading(
            run=run,
            timestamp=timestamp,
            temperature=temp,
            humidity=hum,
            light_level=light,
            latitude=lat,
            longitude=lng,
            event_status="Normal"
        )
        readings.append(reading)
    
    # Bulk create for efficiency
    SensorReading.objects.bulk_create(readings)
    
    # Update run start/end times based on readings
    run.started_at = readings[0].timestamp
    run.ended_at = readings[-1].timestamp
    run.save()
    
    print(f"Successfully populated Run #{run.id} ('medicine') with {len(readings)} readings.")

if __name__ == "__main__":
    populate()
