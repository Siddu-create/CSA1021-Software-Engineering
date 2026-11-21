"""Small deterministic demonstrator for the Smart Campus Facility Platform."""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional



@dataclass
class Booking:
    booking_id: str
    facility: str
    date: str  # YYYY-MM-DD
    start: str  # HH:MM
    end: str    # HH:MM
    user_id: str
    purpose: str


@dataclass
class MaintenanceTicket:
    ticket_id: str
    description: str
    severity: str
    status: str = "Open"
    priority: str = ""


class SmartCampusDemo:
    """In-memory, rule-based demonstration. Not production software."""
    SCORE_RULES = {"excellent": 10, "good": 8, "average": 6, "poor": 3}
    VALID_SEVERITIES = {"low", "medium", "high", "critical"}



    def __init__(self):
        self.bookings = []
        self.tickets = []
        self.audit_log = []



    def _audit(self, action, details):
        self.audit_log.append({"action": action, "details": details})



    @staticmethod
    def _to_minutes(value):
        try:
            parsed = datetime.strptime(value, "%H:%M")
            return parsed.hour * 60 + parsed.minute
        except (ValueError, TypeError):
            raise ValueError("Time must be in HH:MM format")



    def book_facility(self, booking: Booking):
        if not all([booking.booking_id, booking.facility, booking.date, booking.user_id, booking.purpose]):
            raise ValueError("All booking fields are required")
        try:
            datetime.strptime(booking.date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        start, end = self._to_minutes(booking.start), self._to_minutes(booking.end)
        if start >= end:
            raise ValueError("End time must be after start time")
        if end - start > 180:
            raise ValueError("Booking duration cannot exceed 180 minutes")
        for existing in self.bookings:
            if existing.facility == booking.facility and existing.date == booking.date:
                old_start, old_end = self._to_minutes(existing.start), self._to_minutes(existing.end)
                if start < old_end and end > old_start:
                    raise ValueError("Facility booking overlaps an existing booking")
        self.bookings.append(booking)
        self._audit("booking_created", booking.booking_id)
        return {"accepted": True, "booking_id": booking.booking_id}



    def evaluate_answer(self, answer_category, max_marks=10):
        category = str(answer_category).strip().lower()
        if category not in self.SCORE_RULES:
            raise ValueError("Category must be excellent, good, average, or poor")
        if not isinstance(max_marks, int) or max_marks <= 0:
            raise ValueError("Maximum marks must be a positive integer")
        score = min(self.SCORE_RULES[category], max_marks)
        self._audit("answer_scored", f"{category}:{score}/{max_marks}")
        return score



    def compare_marks(self, reference, system_mark, threshold=2):
        if not all(isinstance(value, int) and value >= 0 for value in (reference, system_mark, threshold)):
            raise ValueError("Marks and threshold must be non-negative integers")
        discrepancy = abs(reference - system_mark)
        return {"reference": reference, "system_mark": system_mark, "discrepancy": discrepancy,
                "moderation_required": discrepancy >= threshold}



    def create_ticket(self, ticket_id, description, severity):
        severity = str(severity).strip().lower()
        if not ticket_id or not description.strip():
            raise ValueError("Ticket ID and description are required")
        if severity not in self.VALID_SEVERITIES:
            raise ValueError("Severity must be low, medium, high, or critical")
        priority = {"low": "Low", "medium": "Medium", "high": "High", "critical": "Urgent"}[severity]
        ticket = MaintenanceTicket(ticket_id, description, severity, "Open", priority)
        self.tickets.append(ticket)
        self._audit("ticket_created", ticket_id)
        return asdict(ticket)



    def update_ticket_status(self, ticket_id, status):
        allowed = {"Open", "In Progress", "Resolved", "Closed"}
        if status not in allowed:
            raise ValueError("Invalid ticket status")
        for ticket in self.tickets:
            if ticket.ticket_id == ticket_id:
                ticket.status = status
                self._audit("ticket_status_updated", f"{ticket_id}:{status}")
                return asdict(ticket)
        raise KeyError("Ticket not found")



    def correct_mark(self, student_id, old_mark, new_mark, reason, authorized=False):
        if not authorized:
            raise PermissionError("Only an authorized examiner may correct marks")
        if not reason.strip():
            raise ValueError("Correction reason is required")
        if any(not isinstance(mark, int) or mark < 0 or mark > 10 for mark in (old_mark, new_mark)):
            raise ValueError("Marks must be between 0 and 10")
        self._audit("mark_corrected", f"{student_id}:{old_mark}->{new_mark};reason={reason}")
        return {"student_id": student_id, "old_mark": old_mark, "new_mark": new_mark, "reason": reason}
