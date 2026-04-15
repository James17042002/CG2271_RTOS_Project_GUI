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

    temp_threshold = models.FloatField(default=0.0)
    humidity_threshold = models.FloatField(default=0.0)
    light_threshold = models.FloatField(default=0.0)

    shock_count = models.IntegerField(default=0)
    box_open_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Run #{self.id} - {self.object}"

    @property
    def temp_violations(self):
        return self.readings.filter(temperature__gt=self.temp_threshold).count()

    @property
    def humidity_violations(self):
        return self.readings.filter(humidity__gt=self.humidity_threshold).count()

    @property
    def light_violations(self):
        return self.readings.filter(light_level__gt=self.light_threshold).count()


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
