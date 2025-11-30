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
reminder_df = None  # stores reminders in memory

# Track current selected employee
current_employee_id = None

# Color for highlighting expiring certifications (may not work in all terminals)
COLOR_HIGHLIGHT = "\033[93m"
COLOR_RESET = "\033[0m"


# ---------------------------
#   SAFE DATE PARSER
# ---------------------------
def parse_date_safe(value):
    """
    Try multiple date formats so Option 5 doesn't crash.
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
    """
    Text banner showing currently selected employee, or None.
    """
    global employees_df, current_employee_id

    if employees_df is None or current_employee_id is None:
        return "Currently selected employee: None"

    row = employees_df[employees_df["employee_id"] == current_employee_id]
    if row.empty:
        return "Currently selected employee: None"

    first_name = row.iloc[0]["first_name"]
    last_name = row.iloc[0]["last_name"]
    return f"Currently selected employee: {first_name} {last_name} (ID {current_employee_id})"


# ---------------------------
#   LOADING CSV DATA
# ---------------------------
def load_data():
    """
    Load all CSV files into global DataFrames and reset current employee.
    """
    global employees_df, certifications_df, needs_df, has_df, reminder_df, current_employee_id

    print("Reading data...")

    employees_df = pd.read_csv("employees.csv")
    certifications_df = pd.read_csv("certifications.csv")
    needs_df = pd.read_csv("needs_certifications.csv")
    has_df = pd.read_csv("has_certifications.csv")

    # Load reminders; ensure 'sent_date' exists.
    try:
        reminder_df = pd.read_csv("reminder.csv")
        if "sent_date" not in reminder_df.columns:
            reminder_df["sent_date"] = pd.NA
    except FileNotFoundError:
        reminder_df = pd.DataFrame(
            columns=["employee_id", "certification_id", "reminder_date", "sent_date"]
        )

    current_employee_id = None

    print("Data loaded successfully.")
    print("Current employee selection cleared.\n")


def load_data_if_needed():
    """
    Lazy-load data if user forgot to run option 1.
    """
    if employees_df is None:
        print("Data not loaded yet. Loading now...")
        load_data()


# ---------------------------
#   OPTION 2 — SELECT EMPLOYEE & VIEW CERTS
# ---------------------------
def view_employee_certifications():
    """
    Show a list of employees, let user pick one by ID,
    display that employee's certifications and remember them as 'current'.
    """
    global employees_df, certifications_df, has_df, current_employee_id

    if employees_df is None or has_df is None or certifications_df is None:
        print(" Please load data first (option 1).\n")
        return

    print("\nAvailable Employees:\n")
    cols = ["employee_id", "first_name", "last_name", "employment_status"]
    cols = [c for c in cols if c in employees_df.columns]
    print(employees_df[cols].sort_values(by="employee_id").to_string(index=False))
    print()

    emp_id = read_data.get_integer("Enter employee ID from the list above: ", 1, 999)

    row = employees_df[employees_df["employee_id"] == emp_id]
    if row.empty:
        print("No employee with that ID.\n")
        return

    current_employee_id = emp_id
    name = f"{row.iloc[0]['first_name']} {row.iloc[0]['last_name']}"

    print(f"\nCertifications for {name} (ID {emp_id}):")

    merged = has_df.merge(certifications_df, on="certification_id", how="inner")
    certs = merged[merged["employee_id"] == emp_id]

    if certs.empty:
        print("  – No certifications on record.\n")
    else:
        for _, c in certs.iterrows():
            print(
                f"  - {c['name']} (obtained {c['obtained_date']}, "
                f"expires {c['expiry_date']})"
            )
        print()


# ---------------------------
#   OPTION 3 — CERTS FOR SELECTED EMPLOYEE (+ ADD/REMOVE)
# ---------------------------
def add_certification(emp_id: int):
    """
    Add a certification record for the given employee.
    """
    global has_df

    cert_id = read_data.get_integer("Enter certification ID: ", 1, 999)
    obtained = input("Enter obtained date (YYYY-MM-DD): ")
    expiry = input("Enter expiry date (YYYY-MM-DD or MM/DD/YY): ")

    confirm = input("Confirm add? (Y/N): ").upper()
    if confirm != "Y":
        print("Add cancelled.\n")
        return

    new_row = {
        "employee_id": emp_id,
        "certification_id": cert_id,
        "obtained_date": obtained,
        "expiry_date": expiry,
    }
    has_df = pd.concat([has_df, pd.DataFrame([new_row])], ignore_index=True)
    print("Certification added for employee.\n")


def remove_certification(emp_id: int):
    """
    Remove a certification record for the given employee.
    """
    global has_df, certifications_df

    emp_rows = has_df[has_df["employee_id"] == emp_id]
    if emp_rows.empty:
        print("This employee has no certifications to remove.\n")
        return

    merged = emp_rows.merge(certifications_df, on="certification_id", how="left")
    print("\nCurrent certifications for this employee:")
    print(
        merged[["certification_id", "name", "obtained_date", "expiry_date"]]
        .to_string(index=False)
    )
    print()

    cert_to_remove = read_data.get_integer(
        "Enter certification ID to remove from this employee: ", 1, 999
    )

    mask = (has_df["employee_id"] == emp_id) & (
        has_df["certification_id"] == cert_to_remove
    )
    if not mask.any():
        print("No matching certification record found for this employee.\n")
        return

    confirm = input(
        f"Are you sure you want to remove certification {cert_to_remove} "
        f"from employee {emp_id}? (Y/N): "
    ).upper()
    if confirm != "Y":
        print("Remove cancelled.\n")
        return

    has_df = has_df[~mask].reset_index(drop=True)
    print("Certification removed for employee.\n")


def view_certifications_employee_has():
    """
    Option 3:
    Show what certifications the CURRENTLY SELECTED employee has,
    and allow adding/removing certifications.
    """
    global current_employee_id, employees_df, has_df, certifications_df

    if current_employee_id is None:
        print(" No employee is currently selected. Use option 2 first.\n")
        return

    row = employees_df[employees_df["employee_id"] == current_employee_id]
    if row.empty:
        print("The selected employee no longer exists in the data.\n")
        return

    name = f"{row.iloc[0]['first_name']} {row.iloc[0]['last_name']}"

    merged = has_df.merge(certifications_df, on="certification_id", how="inner")
    certs = merged[merged["employee_id"] == current_employee_id]

    print(f"\nCertifications for {name} (ID {current_employee_id}):")

    if certs.empty:
        print("  – No certifications on record for this employee.\n")
    else:
        for _, c in certs.iterrows():
            print(
                f"  - {c['name']} (obtained {c['obtained_date']}, "
                f"expires {c['expiry_date']})"
            )
        print()

    print("Actions:")
    print("  A - Add a certification for this employee")
    print("  R - Remove a certification from this employee")
    print("  Enter - Return to menu")
    choice = input("Choose an action (A/R or press Enter to skip): ").strip().upper()

    if choice == "A":
        add_certification(current_employee_id)
    elif choice == "R":
        remove_certification(current_employee_id)
    else:
        print("No changes made.\n")


# ---------------------------
#   OPTION 4 — NEEDS FOR SELECTED EMPLOYEE
# ---------------------------
def view_certifications_employee_needs():
    """
    Option 4:
    Show what certifications the CURRENTLY SELECTED employee needs.
    """
    global current_employee_id, employees_df, needs_df, certifications_df

    if current_employee_id is None:
        print(" No employee is currently selected. Use option 2 first.\n")
        return

    if needs_df is None or certifications_df is None or employees_df is None:
        print(" Please load data first (option 1).\n")
        return

    row = employees_df[employees_df["employee_id"] == current_employee_id]
    if row.empty:
        print("The selected employee no longer exists in the data.\n")
        return

    name = f"{row.iloc[0]['first_name']} {row.iloc[0]['last_name']}"

    merged = needs_df.merge(certifications_df, on="certification_id", how="left")
    employee_needs = merged[merged["employee_id"] == current_employee_id]

    print(f"\nCertification needs for {name} (ID {current_employee_id}):")

    if employee_needs.empty:
        print("  – No outstanding certification needs for this employee.\n")
    else:
        for _, r in employee_needs.iterrows():
            print(f"  - {r['name']}")
        print()


# ---------------------------
#   OPTION 5 — EXPIRING CERTIFICATIONS FOR SELECTED EMPLOYEE
# ---------------------------
def reminders_for_employee_certifications():
    """
    Option 5:
    Show certifications for the CURRENTLY SELECTED employee that expire
    in the next 30 days, highlight them, and record reminders.
    """
    global has_df, certifications_df, reminder_df, current_employee_id

    if current_employee_id is None:
        print(" Please select an employee first (option 2).\n")
        return

    if has_df is None or certifications_df is None:
        print(" Please load data first (option 1).\n")
        return

    df = has_df.copy()
    df["expiry_date"] = df["expiry_date"].apply(parse_date_safe)

    today = date.today()
    threshold = today + timedelta(days=30)

    expiring = df[
        (df["employee_id"] == current_employee_id)
        & (df["expiry_date"].notna())
        & (df["expiry_date"] <= threshold)
    ]

    row = employees_df[employees_df["employee_id"] == current_employee_id]
    if row.empty:
        print("The selected employee no longer exists in the data.\n")
        return

    name = f"{row.iloc[0]['first_name']} {row.iloc[0]['last_name']}"

    if expiring.empty:
        print(f"No certifications for {name} are expiring in the next 30 days.\n")
        return

    merged = expiring.merge(certifications_df, on="certification_id", how="left")

    print(f"\n{COLOR_HIGHLIGHT}Certifications expiring soon for {name}:{COLOR_RESET}")
    for _, r in merged.iterrows():
        print(
            f"{COLOR_HIGHLIGHT}  - {r['name']} (expires {r['expiry_date']}){COLOR_RESET}"
        )
    print()

    new_rows = [
        {
            "employee_id": int(r["employee_id"]),
            "certification_id": int(r["certification_id"]),
            "reminder_date": today.isoformat(),
            "sent_date": pd.NA,
        }
        for _, r in expiring.iterrows()
    ]

    reminder_df = pd.concat([reminder_df, pd.DataFrame(new_rows)], ignore_index=True)
    print(f"{len(new_rows)} reminder(s) recorded. Use option 6 to send, option 7 to save.\n")


# ---------------------------
#   OPTION 6 — SEND RENEWAL EMAILS & MARK SENT
# ---------------------------
def send_request_for_renewal():
    """
    Option 6:
    Simulate sending renewal emails for reminders that have not been sent yet.
    Marks sent_date and writes reminder.csv immediately.
    """
    global reminder_df

    if reminder_df is None or reminder_df.empty:
        print("No reminders available. Run option 5 first.\n")
        return

    unsent_mask = reminder_df["sent_date"].isna() | (reminder_df["sent_date"] == "")
    unsent = reminder_df[unsent_mask]

    if unsent.empty:
        print("All recorded reminders have already been sent.\n")
        return

    count = len(unsent)
    confirm = input(
        f"Send renewal request emails for {count} reminder(s)? (Y/N): "
    ).upper()
    if confirm != "Y":
        print("Sending emails cancelled.\n")
        return

    print("Sending renewal request emails (simulated)...")
    print(f"Requests sent for {count} reminder(s).\n")

    today_str = date.today().isoformat()
    reminder_df.loc[unsent_mask, "sent_date"] = today_str

    # Immediately update reminder.csv so history is recorded
    reminder_df.to_csv("reminder.csv", index=False)
    print("Reminder statuses updated in reminder.csv.\n")


# ---------------------------
#   OPTION 7 — SAVE CHANGES
# ---------------------------
def save_changes():
    """
    Option 7:
    Save all dataframes back to CSV files.
    """
    global employees_df, certifications_df, needs_df, has_df, reminder_df

    confirm = input(
        "Save all changes to CSV files (including reminders)? (Y/N): "
    ).upper()
    if confirm != "Y":
        print("Save cancelled.\n")
        return

    employees_df.to_csv("employees.csv", index=False)
    certifications_df.to_csv("certifications.csv", index=False)
    needs_df.to_csv("needs_certifications.csv", index=False)
    has_df.to_csv("has_certifications.csv", index=False)
    reminder_df.to_csv("reminder.csv", index=False)

    print("All changes saved successfully.\n")


# ---------------------------
#   OPTION 8 — VIEW REMINDER LOG
# ---------------------------
def view_reminder_log():
    """
    Option 8:
    Show all reminder records (who, what, when reminded, when sent).
    """
    global reminder_df, employees_df, certifications_df

    if reminder_df is None or reminder_df.empty:
        print("No reminders have been recorded yet.\n")
        return

    print("\nReminder Log:")
    print("-------------")

    merged = (
        reminder_df
        .merge(employees_df, on="employee_id", how="left")
        .merge(certifications_df, on="certification_id", how="left")
    )

    cols = [
        "employee_id", "first_name", "last_name",
        "certification_id", "name",
        "reminder_date", "sent_date",
    ]

    print(merged[cols].to_string(index=False))
    print()


# ---------------------------
#   OPTION 9 — CLEAR SENT REMINDERS
# ---------------------------
def clear_sent_reminders():
    """
    Option 9:
    Remove all reminders that have already been sent
    (i.e., have a non-empty sent_date) from reminder_df and reminder.csv.
    """
    global reminder_df

    if reminder_df is None or reminder_df.empty:
        print("No reminders to clear.\n")
        return

    sent_mask = reminder_df["sent_date"].notna() & (reminder_df["sent_date"] != "")
    sent_count = sent_mask.sum()

    if sent_count == 0:
        print("There are no sent reminders to clear.\n")
        return

    confirm = input(
        f"Clear {sent_count} sent reminder(s) from the log? (Y/N): "
    ).upper()
    if confirm != "Y":
        print("Clear cancelled.\n")
        return

    # Keep only rows that are NOT sent
    reminder_df = reminder_df[~sent_mask].reset_index(drop=True)
    reminder_df.to_csv("reminder.csv", index=False)
    print(f"{sent_count} sent reminder(s) removed from reminder.csv.\n")


# ---------------------------
#   MAIN MENU
# ---------------------------
def main():
    menu_text = """
We Build Stuff HRIS menu
=============================

1. Read data
2. View employee certifications (select employee)
3. View certifications employee has (selected employee, add/remove)
4. View certifications employee needs (selected employee)
5. Expiring certifications (selected employee, record reminders)
6. Send renewal emails (for unsent reminders)
7. Save changes
8. View reminder log
9. Clear sent reminders
10. Exit

=============================
"""

    while True:
        print(get_current_employee_label())
        print(menu_text)

        user_choice = read_data.get_integer("Enter your choice: ", 1, 10)
        clear_screen()

        if user_choice == 1:
            load_data()
        elif user_choice == 2:
            load_data_if_needed()
            view_employee_certifications()
        elif user_choice == 3:
            load_data_if_needed()
            view_certifications_employee_has()
        elif user_choice == 4:
            load_data_if_needed()
            view_certifications_employee_needs()
        elif user_choice == 5:
            load_data_if_needed()
            reminders_for_employee_certifications()
        elif user_choice == 6:
            send_request_for_renewal()
        elif user_choice == 7:
            save_changes()
        elif user_choice == 8:
            load_data_if_needed()
            view_reminder_log()
        elif user_choice == 9:
            clear_sent_reminders()
        elif user_choice == 10:
            if input("Exit program? (Y/N): ").upper() == "Y":
                print("Goodbye!")
                break


if __name__ == "__main__":
    main()
