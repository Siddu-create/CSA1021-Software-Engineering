from django.db import IntegrityError, transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Facility, Booking, MaintenanceTicket, SensorEvent
from .serializers import (
    FacilitySerializer,
    BookingSerializer,
    MaintenanceTicketSerializer,
    SensorEventSerializer,
)
from .permissions import IsStaffOrReadOnly


class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer
    permission_classes = [IsStaffOrReadOnly]


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        booking = self.get_object()

        if not request.user.is_staff:
            return Response(
                {"error": "Only authorized staff can approve bookings."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if booking.facility.restricted and not request.user.is_superuser:
            return Response(
                {"error": "Administrator approval required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        booking.status = "APPROVED"
        booking.save(update_fields=["status"])
        return Response({"status": "APPROVED"})


class MaintenanceTicketViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceTicket.objects.all()
    serializer_class = MaintenanceTicketSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        ticket = self.get_object()

        if not request.user.is_staff:
            return Response(
                {"error": "Staff permission required."},
                status=status.HTTP_403_FORBIDDEN,
            )

        ticket.status = "RESOLVED"
        ticket.save(update_fields=["status", "updated_at"])
        return Response({"status": ticket.status})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def receive_sensor_event(request):
    serializer = SensorEventSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        with transaction.atomic():
            event = serializer.save()
    except IntegrityError:
        return Response(
            {"message": "Duplicate event ignored."},
            status=status.HTTP_200_OK,
        )

    # Simple deterministic priority suggestion, not machine learning.
    description = event.description.lower()
    priority = "CRITICAL" if "fire" in description else (
        "HIGH" if "leak" in description or "failure" in description
        else "MEDIUM"
    )

    ticket = MaintenanceTicket.objects.create(
        facility=event.facility,
        title=f"Sensor alert: {event.event_type}",
        description=event.description,
        priority=priority,
    )

    return Response(
        {
            "message": "Sensor event recorded.",
            "ticket_id": ticket.id,
            "suggested_priority": priority,
        },
        status=status.HTTP_201_CREATED,
    )
