import unittest
from smart_campus.core import SmartCampusDemo, Booking



class SmartCampusTests(unittest.TestCase):
    def setUp(self):
        self.app = SmartCampusDemo()

        self.booking = Booking("B1", "Lab 1", "2026-11-25", "10:00", "11:00", "U1", "Class")



    def test_booking_accepts_valid_request(self):
        self.assertTrue(self.app.book_facility(self.booking)["accepted"])



    def test_overlapping_booking_rejected(self):
        self.app.book_facility(self.booking)
        other = Booking("B2", "Lab 1", "2026-11-25", "10:30", "11:30", "U2", "Practice")
        with self.assertRaisesRegex(ValueError, "overlaps"):
            self.app.book_facility(other)



    def test_non_overlapping_booking_allowed(self):
        self.app.book_facility(self.booking)
        other = Booking("B2", "Lab 1", "2026-11-25", "11:00", "12:00", "U2", "Practice")
        self.assertTrue(self.app.book_facility(other)["accepted"])



    def test_invalid_time_rejected(self):
        invalid = Booking("B3", "Lab 1", "2026-11-25", "13:00", "12:00", "U3", "Test")
        with self.assertRaises(ValueError):
            self.app.book_facility(invalid)



    def test_booking_duration_limit(self):
        long_booking = Booking("B4", "Lab 1", "2026-11-25", "09:00", "13:00", "U4", "Event")
        with self.assertRaisesRegex(ValueError, "180"):
            self.app.book_facility(long_booking)



    def test_deterministic_rule_score(self):
        self.assertEqual(self.app.evaluate_answer("good"), 8)
        self.assertEqual(self.app.evaluate_answer("good"), 8)



    def test_unknown_category_rejected(self):
        with self.assertRaises(ValueError):
            self.app.evaluate_answer("unknown")



    def test_moderation_flag_at_threshold(self):
        result = self.app.compare_marks(8, 6, threshold=2)
        self.assertTrue(result["moderation_required"])



    def test_low_discrepancy_not_flagged(self):
        result = self.app.compare_marks(7, 6, threshold=2)
        self.assertFalse(result["moderation_required"])



    def test_ticket_priority_and_status_update(self):
        ticket = self.app.create_ticket("M1", "Broken projector", "critical")
        self.assertEqual(ticket["priority"], "Urgent")
        updated = self.app.update_ticket_status("M1", "In Progress")
        self.assertEqual(updated["status"], "In Progress")



    def test_invalid_ticket_severity_rejected(self):
        with self.assertRaises(ValueError):
            self.app.create_ticket("M2", "Broken chair", "extreme")



    def test_mark_correction_requires_authorization_and_reason(self):
        with self.assertRaises(PermissionError):
            self.app.correct_mark("STU1", 5, 7, "Correction", authorized=False)
        with self.assertRaises(ValueError):
            self.app.correct_mark("STU1", 5, 7, "", authorized=True)
        result = self.app.correct_mark("STU1", 5, 7, "Examiner review", authorized=True)
        self.assertEqual(result["new_mark"], 7)



    def test_audit_records_actions(self):
        self.app.book_facility(self.booking)
        self.assertEqual(self.app.audit_log[-1]["action"], "booking_created")



if __name__ == "__main__":
    unittest.main()
