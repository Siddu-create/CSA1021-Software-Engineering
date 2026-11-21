"""Deterministic, standard-library-only demonstrator components."""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List



@dataclass
class Booking:
    facility: str
    date: str
    start: str
    end: str
    user_id: str
    purpose: str



@dataclass
class Ticket:
    ticket_id: str
    description: str
    priority: str
    status: str = "Open"



class SmartCampusDemo:
    def __init__(self):
        self.bookings: List[Booking] = []
        self.tickets: Dict[str, Ticket] = {}
        self.audit: List[dict] = []

    def _log(self, action: str, detail: str):
        self.audit.append({"timestamp": datetime.now().isoformat(timespec="seconds"), "action": action, "detail": detail})

    @staticmethod
    def _time_minutes(value: str) -> int:
        try:
            parsed = datetime.strptime(value, "%H:%M")
            return parsed.hour * 60 + parsed.minute
        except ValueError:
            raise ValueError("Time must use HH:MM (24-hour) format.")



    def book_facility(self, booking: Booking) -> tuple[bool, str]:
        if not all([booking.facility.strip(), booking.date.strip(), booking.user_id.strip(), booking.purpose.strip()]):
            return False, "Required booking fields cannot be empty."
        start, end = self._time_minutes(booking.start), self._time_minutes(booking.end)
        if start >= end:
            return False, "End time must be later than start time."
        for existing in self.bookings:
            if existing.facility == booking.facility and existing.date == booking.date:
                old_start, old_end = self._time_minutes(existing.start), self._time_minutes(existing.end)
                if start < old_end and old_start < end:
                    return False, "Facility is already booked for an overlapping time."
        self.bookings.append(booking)
        self._log("BOOKING_CREATED", f"{booking.facility} {booking.date} {booking.start}-{booking.end} by {booking.user_id}")
        return True, "Booking confirmed."

    @staticmethod
    def evaluate_answer(answer_text: str, rubric_keywords: list[str], max_mark: int = 10) -> dict:
        if not answer_text.strip():
            raise ValueError("Answer cannot be empty.")
        if not rubric_keywords or max_mark <= 0:
            raise ValueError("Rubric keywords and positive maximum mark are required.")
        text = answer_text.lower()
        matched = [keyword for keyword in rubric_keywords if keyword.lower() in text]
        mark = round(max_mark * len(matched) / len(rubric_keywords))
        return {"mark": mark, "max_mark": max_mark, "matched_keywords": matched, "needs_review": mark < max_mark * 0.5}

    def create_ticket(self, ticket_id: str, description: str, priority: str) -> Ticket:
        allowed = {"Low", "Medium", "High", "Critical"}
        if not ticket_id.strip() or not description.strip():
            raise ValueError("Ticket ID and description are required.")
        if priority not in allowed:
            raise ValueError(f"Priority must be one of: {', '.join(sorted(allowed))}.")
        if ticket_id in self.tickets:
            raise ValueError("Ticket ID already exists.")
        ticket = Ticket(ticket_id, description, priority)
        self.tickets[ticket_id] = ticket
        self._log("TICKET_CREATED", f"{ticket_id} priority={priority}")
        return ticket


    def update_ticket_status(self, ticket_id: str, status: str) -> Ticket:
        allowed = {"Open", "In Progress", "Resolved", "Closed"}
        if ticket_id not in self.tickets:
            raise KeyError("Ticket not found.")
        if status not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(sorted(allowed))}.")
        old = self.tickets[ticket_id].status
        self.tickets[ticket_id].status = status
        self._log("TICKET_STATUS_UPDATED", f"{ticket_id}: {old} -> {status}")
        return self.tickets[ticket_id]


    def audit_records(self) -> list[dict]:
        return list(self.audit)
