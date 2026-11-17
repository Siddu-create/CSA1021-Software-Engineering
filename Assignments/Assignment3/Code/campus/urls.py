from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FacilityViewSet,
    BookingViewSet,
    MaintenanceTicketViewSet,
    receive_sensor_event,
)

router = DefaultRouter()
router.register("facilities", FacilityViewSet)
router.register("bookings", BookingViewSet, basename="booking")
router.register("tickets", MaintenanceTicketViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("sensor-events/", receive_sensor_event),
]
