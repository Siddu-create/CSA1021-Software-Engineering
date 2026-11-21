from smart_campus.core import SmartCampusDemo, Booking
import csv
from pathlib import Path



def main():
    app = SmartCampusDemo()
    print("SMART CAMPUS ASSIGNMENT 5 DEMONSTRATOR")
    print("======================================")
    booking = Booking("B001", "Computer Lab CL2", "2026-11-25", "10:00", "12:00", "STU1001", "AI lab practice")
    print("Booking:", app.book_facility(booking))
    try:
        overlap = Booking("B002", "Computer Lab CL2", "2026-11-25", "11:00", "12:30", "STU1002", "Project work")
        app.book_facility(overlap)
    except ValueError as error:
        print("Overlap validation:", error)
    print("Rule score for 'good':", app.evaluate_answer("good"), "/ 10")
    print("Mark comparison:", app.compare_marks(8, 6, threshold=2))
    ticket = app.create_ticket("M001", "Projector not working in Lab CL2", "high")
    print("Maintenance ticket:", ticket)
    app.update_ticket_status("M001", "In Progress")
    print("Updated ticket:", app.tickets[0])
    print("Audit records:", len(app.audit_log))
    # Compare deterministic scoring with reference marks using the synthetic CSV.
    csv_path = Path(__file__).parent / "data" / "synthetic_evaluation.csv"
    total, matches, moderation = 0, 0, 0
    print("\nSynthetic evaluation comparison:")
    with csv_path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            system_score = app.evaluate_answer(row["answer_category"], int(row["max_marks"]))
            reference = int(row["reference_mark"])
            comparison = app.compare_marks(reference, system_score, threshold=2)
            total += 1
            matches += reference == system_score
            moderation += comparison["moderation_required"]
            print(f"{row['student_id']}: reference={reference}, rule={system_score}, difference={comparison['discrepancy']}, moderation={comparison['moderation_required']}")
    print(f"\nBaseline exact agreement: {matches}/{total} ({matches/total:.0%})")
    print(f"Cases requiring moderation (difference >= 2): {moderation}")
    print("Note: Synthetic, illustrative data; not an executed institutional evaluation.")


if __name__ == "__main__":
    main()
