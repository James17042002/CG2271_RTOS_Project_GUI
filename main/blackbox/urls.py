from django.urls import path
from .views import HomeView, start_run_page, toggle_run, live_readings, RunListView, run_detail

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("runs/", RunListView.as_view(), name="run_list"),
    path("runs/<int:pk>/", run_detail, name="run_detail"),
    path("start-run/", start_run_page, name="start_run_page"),
    path("toggle-run/", toggle_run, name="toggle_run"),
    path("live-readings/", live_readings, name="live_readings"),
]
