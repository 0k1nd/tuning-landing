from django.urls import path

from .views import IndexView, LeadCreateView

app_name = "main"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("leads/", LeadCreateView.as_view(), name="lead_create"),
]
