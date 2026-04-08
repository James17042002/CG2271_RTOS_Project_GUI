import django_filters
from django import forms
from .models import Run

class RunFilter(django_filters.FilterSet):
    object = django_filters.CharFilter(lookup_expr='icontains', label='Object Name')
    started_before = django_filters.DateTimeFilter(
        field_name='started_at', 
        lookup_expr='lte', 
        label='Started Before',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    
    class Meta:
        model = Run
        fields = ['object', 'is_active', 'started_before']
