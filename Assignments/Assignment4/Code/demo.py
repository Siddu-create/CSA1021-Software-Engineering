from smart_campus.core import SmartCampusDemo, Booking



def main():
    system = SmartCampusDemo()
    print("SMART CAMPUS – Assignment 4 Demonstrator\n")

    booking = Booking("Computer Lab - CL2", "2026-11-17", "10:00", "12:00", "STU1001", "AI Lab Practice")
    ok, message = system.book_facility(booking)
    print(f"Booking test: {message}")
    duplicate = Booking("Computer Lab - CL2", "2026-11-17", "11:00", "12:30", "STU1002", "Project work")
    ok2, message2 = system.book_facility(duplicate)
    print(f"Overlap test: {message2}")

    result = system.evaluate_answer("Software engineering uses requirements, design, testing and maintenance.", ["requirements", "design", "testing", "maintenance"])
    print(f"Rule evaluation: {result['mark']}/{result['max_mark']} | matched={result['matched_keywords']} | review={result['needs_review']}")

    ticket = system.create_ticket("MT-001", "Projector display not working in Lab CL2", "High")
    system.update_ticket_status(ticket.ticket_id, "In Progress")
    print(f"Maintenance ticket: {ticket.ticket_id} | {ticket.priority} | {ticket.status}")
    print(f"Audit entries recorded: {len(system.audit_records())}")

if __name__ == "__main__":
    main()
