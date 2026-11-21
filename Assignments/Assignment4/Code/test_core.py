import unittest
from smart_campus.core import SmartCampusDemo, Booking



class TestSmartCampusDemo(unittest.TestCase):
    def setUp(self):
        self.app = SmartCampusDemo()

        self.booking = Booking("Lab CL2", "2026-11-17", "10:00", "12:00", "STU1", "Practice")

    def test_valid_booking_accepted(self):
        self.assertTrue(self.app.book_facility(self.booking)[0])

    def test_overlapping_booking_rejected(self):
        self.app.book_facility(self.booking)
        overlap = Booking("Lab CL2", "2026-11-17", "11:00", "13:00", "STU2", "Practice")
        self.assertFalse(self.app.book_facility(overlap)[0])

    def test_adjacent_booking_allowed(self):
        self.app.book_facility(self.booking)
        adjacent = Booking("Lab CL2", "2026-11-17", "12:00", "13:00", "STU2", "Practice")
        self.assertTrue(self.app.book_facility(adjacent)[0])

    def test_invalid_time_order_rejected(self):
        invalid = Booking("Lab CL2", "2026-11-17", "13:00", "12:00", "STU1", "Practice")
        self.assertFalse(self.app.book_facility(invalid)[0])

    def test_empty_booking_field_rejected(self):
        invalid = Booking("", "2026-11-17", "10:00", "12:00", "STU1", "Practice")
        self.assertFalse(self.app.book_facility(invalid)[0])

    def test_rule_evaluation_repeatable(self):
        answer = "requirements design testing maintenance"
        rubric = ["requirements", "design", "testing", "maintenance"]
        first = self.app.evaluate_answer(answer, rubric)
        second = self.app.evaluate_answer(answer, rubric)
        self.assertEqual(first, second)
        self.assertEqual(first["mark"], 10)

    def test_empty_answer_rejected(self):
        with self.assertRaises(ValueError):
            self.app.evaluate_answer("", ["testing"])

    def test_ticket_creation_and_status(self):
        ticket = self.app.create_ticket("MT-1", "Broken projector", "High")
        self.assertEqual(ticket.status, "Open")
        self.app.update_ticket_status("MT-1", "In Progress")
        self.assertEqual(ticket.status, "In Progress")

    def test_invalid_priority_rejected(self):
        with self.assertRaises(ValueError):
            self.app.create_ticket("MT-2", "Broken chair", "Urgent")

    def test_duplicate_ticket_id_rejected(self):
        self.app.create_ticket("MT-3", "Broken chair", "Medium")
        with self.assertRaises(ValueError):
            self.app.create_ticket("MT-3", "Another issue", "Low")

    def test_audit_log_created(self):
        self.app.book_facility(self.booking)
        self.assertEqual(len(self.app.audit_records()), 1)
        self.assertEqual(self.app.audit_records()[0]["action"], "BOOKING_CREATED")


if __name__ == "__main__":
    unittest.main()
