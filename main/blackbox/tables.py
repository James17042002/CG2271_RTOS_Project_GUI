import django_tables2 as tables
from .models import Run
from django.utils.html import format_html

class RunTable(tables.Table):
    started_at = tables.DateTimeColumn(format="d/m/y g:i A")
    ended_at = tables.DateTimeColumn(format="d/m/y g:i A")
    # A placeholder details link for now
    details = tables.Column(empty_values=(), verbose_name="Details", orderable=False)
    
    class Meta:
        model = Run
        template_name = "django_tables2/bootstrap5.html"
        fields = ("id", "object", "is_active", "started_at", "temp_violations", "humidity_violations", "light_violations")
        attrs = {"class": "table table-hover shadow-sm rounded"}

    def render_details(self, record):
        from django.urls import reverse
        url = reverse("run_detail", args=[record.pk])
        return format_html('<a href="{}" class="btn btn-sm btn-outline-primary px-3 rounded-pill">{}</a>', url, 'View Details')

    def render_is_active(self, value):
        if value:
            return format_html('<span class="badge bg-success">{}</span>', 'Active')
        return format_html('<span class="badge bg-secondary">{}</span>', 'Completed')
