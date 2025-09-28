from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StaffProfileViewSet

router = DefaultRouter()
app_name = "app_hr"

router.register(r"staff-profiles", StaffProfileViewSet, basename="hr-staff-profiles")

urlpatterns = [
    path("", include(router.urls)),
]