
from django.conf import settings
from django.db import models


class Facility(models.Model):
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    restricted = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("CANCELLED", "Cancelled"),
    ]

    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    purpose = models.CharField(max_length=250)
    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default="PENDING"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_time"]


class MaintenanceTicket(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("ASSIGNED", "Assigned"),
        ("IN_PROGRESS", "In Progress"),
        ("RESOLVED", "Resolved"),
        ("CLOSED", "Closed"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("CRITICAL", "Critical"),
    ]

    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField()
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="MEDIUM"
    )
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="OPEN"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SensorEvent(models.Model):
    event_id = models.CharField(max_length=120, unique=True)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=80)
    description = models.TextField(blank=True)
    received_at = models.DateTimeField(auto_now_add=True)
