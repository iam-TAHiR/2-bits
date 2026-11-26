"""SAKHI — Resettable Fictional Demonstration Dataset Seeder.

Populates backend/asha_data.db with 20 coherent, fictional households
demonstrating every priority tier (RED, ORANGE, YELLOW Overdue/Due Today,
GREEN Upcoming/Routine, and Missing Data Verification), maternal/child
records, vaccinations, visits, follow-ups, alerts, and chatbot queries.

NOTE: All names, phone numbers (9000000xxx), and scenarios are 100% FICTIONAL
for hackathon demonstration only. Never runs automatically on app startup.

Usage:
    python seed_demo_data.py --confirm-reset
"""

import argparse
from datetime import date, datetime, timedelta
import json
from pathlib import Path
import sqlite3
import sys

DB_PATH = Path(__file__).resolve().parent / "backend" / "asha_data.db"


def seed_demo(db_path: Path = DB_PATH) -> None:
    today = date.today()
    d_str = lambda delta: (today + timedelta(days=delta)).isoformat()
    d_dmy = lambda delta: (today + timedelta(days=delta)).strftime("%d-%m-%Y")
    ts_past = lambda delta: (today + timedelta(days=delta)).strftime("%Y-%m-%d 10:30:00")

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    # Clear only operational demo tables (preserve asha_workers, keyword1-4, bot_*, note_*)
    cur.execute("DELETE FROM visits")
    cur.execute("DELETE FROM pregnancies")
    cur.execute("DELETE FROM children")
    cur.execute("DELETE FROM home_records")

    # 20 Fictional Households (B_001 .. B_020)
    homes = [
        ("B_001", "Ward 1, Tumkur", "PREGNANT"),
        ("B_002", "Ward 2, Tumkur", "PREGNANT"),
        ("B_003", "Ward 3, Tumkur", "POSTDELIVERY"),
        ("B_004", "Ward 4, Tumkur", "PREGNANT"),
        ("B_005", "Ward 2, Tumkur", "INFANT"),
        ("B_006", "Ward 5, Tumkur", "NEWBORN"),
        ("B_007", "Ward 1, Tumkur", "INFANT"),
        ("B_008", "Ward 3, Tumkur", "PREGNANT"),
        ("B_009", "Ward 4, Tumkur", "INFANT"),
        ("B_010", "Ward 5, Tumkur", "PREGNANT"),
        ("B_011", "Ward 6, Tumkur", "INFANT"),
        ("B_012", "Ward 2, Tumkur", "PREGNANT"),
        ("B_013", "Ward 1, Tumkur", "INFANT"),
        ("B_014", "Ward 6, Tumkur", "PREGNANT"),
        ("B_015", "Ward 3, Tumkur", "INFANT"),
        ("B_016", "Ward 4, Tumkur", "PREGNANT"),
        ("B_017", "Ward 5, Tumkur", "INFANT"),
        ("B_018", "Ward 1, Tumkur", "PREGNANT"),
        ("B_019", "Ward 2, Tumkur", "INFANT"),
        ("B_020", "Ward 6, Tumkur", "PREGNANT"),
    ]
    cur.executemany("INSERT INTO home_records (beneficiary_id, address, status) VALUES (?, ?, ?)", homes)

    # 12 Fictional Maternal / Pregnancy Records
    pregnancies = [
        ("B_001", 34, d_dmy(42), "", "ACTIVE", "{}", '{"Td-2": "' + d_dmy(7) + '"}', "{}", "Meenakshi R", 28, "1998-04-10", "9000000001", 59.0, "O+"),
        ("B_002", 30, d_dmy(70), "", "HIGH_RISK", '{"Td-1": "' + d_dmy(-30) + '"}', '{"Td-2": "' + d_dmy(10) + '"}', "{}", "Kavitha S", 29, "1997-06-15", "9000000002", 61.0, "B+"),
        ("B_004", 24, d_dmy(112), "", "ACTIVE", '{"Td-1": "' + d_dmy(-20) + '"}', "{}", "{}", "Lakshmi N", 26, "2000-02-18", "9000000004", 54.0, "O+"),
        ("B_006", 40, d_dmy(-5), d_dmy(-5), "COMPLETED", '{"Td-1": "' + d_dmy(-60) + '"}', "{}", "{}", "Deepa V", 25, "2001-08-22", "9000000006", 55.0, "A+"),
        ("B_008", 28, d_dmy(84), "", "ACTIVE", '{"Td-1": "' + d_dmy(-25) + '"}', '{"Td-2": "' + d_dmy(0) + '"}', "{}", "Bhavya R", 24, "2002-01-12", "9000000008", 53.0, "AB+"),
        ("B_010", 18, d_dmy(154), "", "ACTIVE", "{}", '{"Td-1": "' + d_dmy(2) + '"}', "{}", "Revathi M", 27, "1999-09-05", "9000000010", 52.0, "B-"),
        ("B_012", 14, d_dmy(182), "", "ACTIVE", "{}", '{"Td-1": "' + d_dmy(5) + '"}', "{}", "Geetha S", 23, "2003-03-14", "9000000012", 50.0, "O-"),
        ("B_014", 16, d_dmy(168), "", "ACTIVE", "{}", None, "{}", "Savitha B", 26, "2000-11-01", "", None, "A+"),  # Missing mobile, weight, vac_due
        ("B_016", 22, d_dmy(126), "", "ACTIVE", '{"Td-1": "' + d_dmy(-15) + '"}', "{}", "{}", "Asha T", 27, "1999-07-19", "9000000016", 56.0, "O+"),
        ("B_018", 26, d_dmy(98), "", "ACTIVE", '{"Td-1": "' + d_dmy(-20) + '"}', "{}", "{}", "Suma R", 28, "1998-12-03", "9000000018", 57.0, "B+"),
        ("B_020", 12, d_dmy(196), "", "ACTIVE", "{}", "{}", "{}", "Rekha V", 25, "2001-05-27", "9000000020", 51.0, "A+"),
        ("B_003", 40, d_dmy(-10), d_dmy(-10), "COMPLETED", '{"Td-1": "' + d_dmy(-90) + '"}', "{}", "{}", "Ananya M", 26, "2000-06-30", "9000000003", 55.0, "B+"),
    ]
    cur.executemany(
        """
        INSERT INTO pregnancies (beneficiary_id, week, exp_dd, dd, status, vacs_taken, vac_due, next_vac_n_due, mother_name, age, dob, mobile, weight, blood_grp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        pregnancies,
    )

    # 14 Fictional Child Records
    children = [
        ("B_003", "Aarav", d_dmy(-10), 10, "Male", 3.2, "BCG, OPV-0", "bOPV-1, Pentavalent-1", "{}", d_str(7), "Suresh M", "Ananya M", "B+"),
        ("B_005", "Rohan", d_dmy(-45), 6, "Male", 4.6, "BCG, OPV-0", "bOPV-1, Pentavalent-1", "{}", d_str(-3), "Karthik K", "Priya K", "O+"),
        ("B_006", "Diya", d_dmy(-5), 1, "Female", 3.0, "BCG", "OPV-0, Hep-B", "{}", d_str(-2), "Vijay V", "Deepa V", "A+"),
        ("B_007", "Vihaan", d_dmy(-275), 9, "Male", 8.1, "BCG, Pentavalent-1, Pentavalent-2", "MR-1, Vitamin A", "{}", d_str(-5), "Prakash P", "Shwetha P", "B+"),
        ("B_009", "Ishaan", d_dmy(-70), 10, "Male", 5.2, "BCG, Pentavalent-1", "Pentavalent-2, bOPV-2", "{}", d_str(0), "Ganesh G", "Sunitha G", "AB+"),
        ("B_011", "Kiran", d_dmy(-98), 14, "Male", 6.0, "BCG, Pentavalent-1, Pentavalent-2", "bOPV-3, Pentavalent-3", "{}", d_str(4), "Kumar K", "Nandini K", "O+"),
        ("B_013", "Anvi", d_dmy(-365), 12, "Female", 9.0, "BCG, MR-1", "PCV-Booster", "{}", d_str(6), "Dinesh D", "Pooja D", "A-"),
        ("B_015", "Vivaan", "", 8, "Male", None, "BCG", "Pentavalent-2", "{}", "", "Ramesh R", "Neha R", "B+"),  # Missing DOB & weight
        ("B_017", "Nithya", d_dmy(-180), 6, "Female", 7.1, "BCG, Pentavalent-1, Pentavalent-2, Pentavalent-3", "", "{}", d_str(30), "Lokesh L", "Padma L", "O+"),
        ("B_019", "Arjun", d_dmy(-210), 7, "Male", 7.6, "BCG, Pentavalent-1, Pentavalent-2, Pentavalent-3", "", "{}", d_str(25), "Naveen N", "Divya N", "A+"),
        ("B_001", "Meera (Child)", d_dmy(-400), 13, "Female", 9.4, "BCG, MR-1", "", "{}", d_str(45), "Raj R", "Meenakshi R", "O+"),
        ("B_002", "Kiranmayi", d_dmy(-500), 16, "Female", 10.2, "BCG, MR-1, DPT-Booster", "", "{}", d_str(60), "Santhosh S", "Kavitha S", "B+"),
        ("B_004", "Tejas", d_dmy(-600), 20, "Male", 11.0, "BCG, MR-1, DPT-Booster", "", "{}", d_str(60), "Nagaraj N", "Lakshmi N", "O+"),
        ("B_016", "Saanvi", d_dmy(-450), 15, "Female", 9.8, "BCG, MR-1", "", "{}", d_str(50), "Tarun T", "Asha T", "O+"),
    ]
    cur.executemany(
        """
        INSERT INTO children (beneficiary_id, child_name, dob, age, gender, weight, vacs_taken, vacs_due, next_vac_n_due, next_visit, father_name, mother_name, blood_grp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        children,
    )

    # 16 Coherent Visits covering RED, ORANGE, Overdue, Due Today, Upcoming, and Completed
    visits = [
        ("V001", "B_001", "Severe dizziness and bleeding reported", "[DEMO] Danger sign recorded: severe dizziness and vaginal bleeding. Immediate PHC/FRU referral.", "ANC Emergency", d_str(0), "", "S"),
        ("V002", "B_002", "BP elevated at clinic", "High-risk pregnancy follow-up: check BP and hemoglobin with ANM.", "ANC", d_str(0), "", "H"),
        ("V003", "B_003", "Post-delivery urgent check", "Post-escalation PNC check completed; verify mother & newborn recovery.", "PNC", d_str(-2), ts_past(-2), "HS"),
        ("V004", "B_004", "", "Routine ANC 24-week follow-up and IFA tablet check.", "ANC", d_str(-4), "", "N"),
        ("V005", "B_005", "", "Pending bOPV-1 and Pentavalent-1 vaccination follow-up.", "Vaccination", d_str(-3), "", "M"),
        ("V006", "B_006", "", "Postnatal Day 5 mother and newborn thermal/weight check.", "PNC", d_str(-2), "", "N"),
        ("V007", "B_007", "", "Pending MR-1 and Vitamin A 1st dose vaccination.", "Vaccination", d_str(-5), "", "M"),
        ("V008", "B_008", "", "Scheduled 28-week ANC checkup and Td-2 reminder.", "ANC", d_str(0), "", "N"),
        ("V009", "B_009", "", "Scheduled Pentavalent-2 vaccination visit today.", "Vaccination", d_str(0), "", "N"),
        ("V010", "B_010", "", "Upcoming 18-week ANC & Td-1 counseling visit.", "ANC", d_str(2), "", "N"),
        ("V011", "B_011", "", "Upcoming 14-week Pentavalent-3 & bOPV-3 immunization.", "Vaccination", d_str(4), "", "N"),
        ("V012", "B_012", "", "Upcoming 14-week ANC Calcium & IFA counseling.", "ANC", d_str(5), "", "N"),
        ("V016", "B_016", "BP 118/76, IFA regular", "Routine ANC visit completed. Mother doing well, taking IFA daily.", "ANC", d_str(-3), ts_past(-3), "N"),
        ("V017", "B_017", "Child feeding well", "Routine 6-month growth & feeding counseling completed.", "GENERAL", d_str(-6), ts_past(-6), "N"),
        ("V018", "B_018", "Vitals normal", "Routine ANC 26-week checkup completed. BP normal.", "ANC", d_str(-4), ts_past(-4), "N"),
        ("V019", "B_019", "Growth normal", "Routine 7-month infant check completed. No fever.", "GENERAL", d_str(-5), ts_past(-5), "N"),
    ]
    cur.executemany(
        "INSERT INTO visits (id, beneficiary_id, voice, note, type, due_date, visit_ts, flag) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        visits,
    )

    conn.commit()
    conn.close()
    print(f"Seeded coherent fictional demo dataset into {db_path}:")
    print(f"  Households: {len(homes)}, Pregnancies: {len(pregnancies)}, Children: {len(children)}, Visits: {len(visits)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset SAKHI database to clean fictional demo dataset.")
    parser.add_argument("--confirm-reset", action="store_true", help="Required flag to confirm resetting demo tables.")
    args = parser.parse_args()
    if not args.confirm_reset:
        print("Aborted: pass --confirm-reset to deliberately reset demo data.")
        sys.exit(1)
    seed_demo()
