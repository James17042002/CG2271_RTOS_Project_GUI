from django.contrib import admin
from .models import Run, SensorReading


from .firebase_utils import sync_active_run_status

@admin.register(Run)
class RunAdmin(admin.ModelAdmin):
    list_display = ("id", "object", "is_active", "started_at", "ended_at")
    list_filter = ("is_active", "started_at", "ended_at")
    search_fields = ("object",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        sync_active_run_status()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        sync_active_run_status()


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ("id", "timestamp", "temperature", "humidity", "light_level", "event_status")
    list_filter = ("timestamp", "run", "event_status")
    search_fields = ("event_status",)
