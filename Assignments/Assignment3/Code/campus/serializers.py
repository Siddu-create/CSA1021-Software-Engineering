from rest_framework import serializers
from .models import Facility, Booking, MaintenanceTicket, SensorEvent


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = "__all__"


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = ("user", "status")

    def validate(self, data):
        start = data["start_time"]
        end = data["end_time"]
        facility = data["facility"]

        if start >= end:
            raise serializers.ValidationError(
                "End time must be after start time."
            )

        if not facility.is_available:
            raise serializers.ValidationError(
                "This facility is unavailable."
            )

        overlapping = Booking.objects.filter(
            facility=facility,
            status__in=["PENDING", "APPROVED"],
            start_time__lt=end,
            end_time__gt=start,
        )

        if self.instance:
            overlapping = overlapping.exclude(pk=self.instance.pk)

        if overlapping.exists():
            raise serializers.ValidationError(
                "This facility is already booked during that time."
            )

        return data


class MaintenanceTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceTicket
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class SensorEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorEvent
        fields = "__all__"
        read_only_fields = ("received_at",)
