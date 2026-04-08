from django.db import models


class Run(models.Model):
    """
    Represents a single 'journey' / recording session.
    A run is 'active' if data is currently being recorded into it.
    """
    object = models.CharField(max_length=200, default="Unnamed Run")
    is_active = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Run #{self.id} - {self.object}"


class SensorReading(models.Model):
    """
    A single telemetry snapshot pushed by the ESP32 via Firebase.
    """
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="readings", null=True, blank=True)
    firebase_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    event_status = models.CharField(max_length=100, blank=True, default="")

    # Sensor fields - adjust field types / names to match ESP32 JSON keys
    temperature = models.FloatField(default=0.0)
    humidity = models.FloatField(default=0.0)
    light_level = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    def __str__(self):
        return (
            f"Reading @ {self.timestamp:%H:%M:%S} | "
            f"Temp={self.temperature}C  Hum={self.humidity}%  "
            f"Light={self.light_level}  GPS=({self.latitude}, {self.longitude})"
        )
