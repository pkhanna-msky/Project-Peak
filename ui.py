"""
This is the user interface for the Human Resources information system
at We Build Stuff.
"""

import os
import pandas as pd
import read_data
from datetime import datetime, timedelta, date


# Global “in-memory” data store
employees_df = None
certifications_df = None
needs_df = None
has_df = None
reminder_df = None

# Track current selected employee
current_employee_id = None

# Color for highlighting expiring certifications
COLOR_HIGHLIGHT = "\033[93m"
COLOR_RESET = "\033[0m"


# ---------------------------
#   SAFE DATE PARSER (FIX)
# ---------------------------
def parse_date_safe(value):
    """
    Try multiple date formats so Option 5 never crashes.
    Supports:
      - YYYY-MM-DD
      - MM/DD/YY
      - MM/DD/YYYY
    Returns a datetime.date or None.
    """
    if pd.isna(value):
        return None

    value = str(value).strip()

    for fmt in ("%Y-%m-%d", "%m/%d/%y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    return None  # If nothing worked


# ---------------------------
#   UTILITY FUNCTIONS
# ---------------------------
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def get_current_employee_label():
    global employees_df, current_employee_id

    if employees_df is None or current_employee_id is None:
        return "Currently selected employee: None"

    row = employees_df[employees_df["employee_id"] == current_employee_id]
    if row.empty:
        return "Currently selected employee: None"

    return (f"Currently selected employee: "
            f"{row.iloc[0]['first_name']} {row.iloc[0]['last_name']} "
            f"(ID {current_employee_id})")


# ---------------------------
#   LOADING CSV DATA
# ---------------------------
def load_data():
    global employees_df, certifications_df, needs_df, has_df, reminder_df, current_employee_id

    print("Reading data...")

    employees_df = pd.read_csv("employees.csv")
    certifications_df = pd.read_csv("certifications.csv")
    needs_df = pd.read_csv("needs_certifications.csv")
    has_df = pd.read_csv("has_certifications.csv")

    try:
        reminder_df = pd.read_csv("reminder.csv")
    except FileNotFoundError:
        reminder_df = pd.DataFrame(columns=["employee_id", "certification_id", "reminder_date"])

    current_employee_id = None
    print("Data loaded successfully. Current employee selection cleared.\n")


def load_data_if_needed():
    if employees_df is None:
        print("Data not loaded yet. Loading now...")
        load_data()


# ---------------------------
#   OPTION 2 — SELECT EMPLOYEE
# ---------------------------
def view_employee_certifications():
    global employees_df, certifications_df, has_df, current_employee_id

    if employees_df is None or has_df is None:
        print("Please load data first (Option 1).\n")
        return

    print("\nAvailable Employees:\n")
    print(employees_df[["employee_id", "first_name", "last_name", "employment_status"]]
          .sort_values(by="employee_id").to_string(index=False))
    print()

    emp_id = read_data.get_integer("Enter employee ID: ", 1, 999)
    row = employees_df[employees_df["employee_id"] == emp_id]

    if row.empty:
        print("No employee with that ID.\n")
        return

    current_employee_id = emp_id
    name = f"{row.iloc[0]['first_name']} {row.iloc[0]['last_name']}"

    print(f"\nCertifications for {name} (ID {emp_id})")

    merged = has_df.merge(certifications_df, on="certification_id", how="inner")
    certs = merged[merged["employee_id"] == emp_id]

    if certs.empty:
        print("  – No certifications on record.\n")
    else:
        for _, c in certs.iterrows():
            print(f"  - {c['name']} (obtained {c['obtained_date']}, expires {c['expiry_date']})")
        print()


# ---------------------------
#   OPTION 3 — CERTS FOR SELECTED EMPLOYEE
# ---------------------------
def add_certification(emp_id):
    global has_df

    cert_id = read_data.get_integer("Enter certification ID: ", 1, 999)
    obtained = input("Enter obtained date (YYYY-MM-DD): ")
    expiry = input("Enter expiry date (YYYY-MM-DD or MM/DD/YY): ")

    if input("Confirm add? (Y/N): ").upper() != "Y":
        print("Cancelled.\n")
        return

    new = {
        "employee_id": emp_id,
        "certification_id": cert_id,
        "obtained_date": obtained,
        "expiry_date": expiry
    }
    has_df = pd.concat([has_df, pd.DataFrame([new])], ignore_index=True)
    print("Certification added.\n")


def remove_certification(emp_id):
    global has_df, certifications_df

    emp_rows = has_df[has_df["employee_id"] == emp_id]
    if emp_rows.empty:
        print("This employee has no certifications.\n")
        return

    merged = emp_rows.merge(certifications_df, on="certification_id")
    print("\nEmployee Certifications:")
    print(merged[["certification_id", "name", "obtained_date", "expiry_date"]]
          .to_string(index=False))
    print()

    cert_id = read_data.get_integer("Enter certification ID to remove: ", 1, 999)
    mask = (has_df["employee_id"] == emp_id) & (has_df["certification_id"] == cert_id)

    if not mask.any():
        print("No such certification for this employee.\n")
        return

    if input("Confirm removal? (Y/N): ").upper() != "Y":
        print("Cancelled.\n")
        return

    has_df = has_df[~mask].reset_index(drop=True)
    print("Certification removed.\n")


def view_certifications_employee_has():
    global current_employee_id, employees_df, has_df, certifications_df

    if current_employee_id is None:
        print("No employee selected. Use Option 2 first.\n")
        return

    row = employees_df[employees_df["employee_id"] == current_employee_id]
    name = f"{row.iloc[0]['first_name']} {row.iloc[0]['last_name']}"

    merged = has_df.merge(certifications_df, on="certification_id")
    certs = merged[merged["employee_id"] == current_employee_id]

    print(f"\nCertifications for {name} (ID {current_employee_id}):")

    if certs.empty:
        print("  – No certifications.\n")
    else:
        for _, c in certs.iterrows():
            print(f"  - {c['name']} (obtained {c['obtained_date']}, expires {c['expiry_date']})")
        print()

    # Sub-menu
    choice = input("A=Add, R=Remove, Enter=Return: ").upper()
    if choice == "A":
        add_certification(current_employee_id)
    elif choice == "R":
        remove_certification(current_employee_id)


# ---------------------------
#   OPTION 4 — NEEDS FOR SELECTED EMPLOYEE
# ---------------------------
def view_certifications_employee_needs():
    global current_employee_id

    if current_employee_id is None:
        print("Select an employee first (Option 2).\n")
        return

    row = employees_df[employees_df["employee_id"] == current_employee_id]
    name = f"{row.iloc[0]['first_name']} {row.iloc[0]['last_name']}"

    merged = needs_df.merge(certifications_df, on="certification_id")
    needs = merged[merged["employee_id"] == current_employee_id]

    print(f"\nNeeded certifications for {name} (ID {current_employee_id}):")
    if needs.empty:
        print("  – No outstanding needs.\n")
    else:
        for _, r in needs.iterrows():
            print(f"  - {r['name']}")
        print()


# ---------------------------
#   OPTION 5 — EXPIRING CERTIFICATIONS (FIXED)
# ---------------------------
def reminders_for_employee_certifications():
    global has_df, certifications_df, reminder_df, current_employee_id

    if current_employee_id is None:
        print("Please select an employee first (Option 2).\n")
        return

    # Copy and parse dates safely
    df = has_df.copy()
    df["expiry_date"] = df["expiry_date"].apply(parse_date_safe)

    today = date.today()
    threshold = today + timedelta(days=30)

    # Filter
    expiring = df[
        (df["employee_id"] == current_employee_id) &
        (df["expiry_date"].notna()) &
        (df["expiry_date"] <= threshold)
    ]

    row = employees_df[employees_df["employee_id"] == current_employee_id]
    name = f"{row.iloc[0]['first_name']} {row.iloc[0]['last_name']}"

    if expiring.empty:
        print(f"No expiring certifications for {name}.\n")
        return

    merged = expiring.merge(certifications_df, on="certification_id")

    print(f"\n{COLOR_HIGHLIGHT}Expiring Soon for {name}:{COLOR_RESET}")
    for _, r in merged.iterrows():
        print(f"{COLOR_HIGHLIGHT}  - {r['name']} (expires {r['expiry_date']}){COLOR_RESET}")
    print()

    # Save reminders temporarily in memory
    new_rows = [{
        "employee_id": int(r["employee_id"]),
        "certification_id": int(r["certification_id"]),
        "reminder_date": today.isoformat()
    } for _, r in expiring.iterrows()]

    reminder_df = pd.concat([reminder_df, pd.DataFrame(new_rows)], ignore_index=True)
    print(f"{len(new_rows)} reminder(s) recorded. Use Option 7 to save.\n")


# ---------------------------
#   OPTION 6 — SEND EMAIL
# ---------------------------
def send_request_for_renewal():
    global reminder_df

    if reminder_df is None or reminder_df.empty:
        print("No reminders available. Run Option 5 first.\n")
        return

    if input("Send renewal emails now? (Y/N): ").upper() != "Y":
        print("Cancelled.\n")
        return

    print(f"Sending {len(reminder_df)} renewal email(s)... (simulated)")
    print("Done.\n")


# ---------------------------
#   OPTION 7 — SAVE CHANGES
# ---------------------------
def save_changes():
    global employees_df, certifications_df, needs_df, has_df, reminder_df

    if input("Save all changes to CSV files? (Y/N): ").upper() != "Y":
        print("Cancelled.\n")
        return

    employees_df.to_csv("employees.csv", index=False)
    certifications_df.to_csv("certifications.csv", index=False)
    needs_df.to_csv("needs_certifications.csv", index=False)
    has_df.to_csv("has_certifications.csv", index=False)
    reminder_df.to_csv("reminder.csv", index=False)

    print("All changes saved successfully.\n")


# ---------------------------
#   MAIN MENU
# ---------------------------
def main():
    menu = """
We Build Stuff HRIS Menu
=============================

1. Read data
2. View employee certifications (select employee)
3. View certifications employee has (selected employee)
4. View certifications employee needs (selected employee)
5. Expiring certifications (selected employee)
6. Send renewal emails
7. Save changes
8. Exit

=============================
"""

    while True:
        print(get_current_employee_label())
        print(menu)

        choice = read_data.get_integer("Enter your choice: ", 1, 8)
        clear_screen()

        if choice == 1:
            load_data()
        elif choice == 2:
            load_data_if_needed()
            view_employee_certifications()
        elif choice == 3:
            load_data_if_needed()
            view_certifications_employee_has()
        elif choice == 4:
            load_data_if_needed()
            view_certifications_employee_needs()
        elif choice == 5:
            load_data_if_needed()
            reminders_for_employee_certifications()
        elif choice == 6:
            send_request_for_renewal()
        elif choice == 7:
            save_changes()
        elif choice == 8:
            if input("Exit program? (Y/N): ").upper() == "Y":
                print("Goodbye!")
                break


if __name__ == "__main__":
    main()
    