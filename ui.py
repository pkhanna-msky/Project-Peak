"""
This is the user interface for the Human Resources information system
at We Build Stuff.
"""

import os
import pandas as pd
import Data_import  # helper module we’ll define below


# Global “in-memory” data store
employees_df = None
certifications_df = None
needs_df = None
has_df = None


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def load_data():
    global employees_df, certifications_df, needs_df, has_df

    print("Reading data...")

    employees_df = pd.read_csv("employees.csv")
    certifications_df = pd.read_csv("certifications.csv")
    needs_df = pd.read_csv("needs_certification.csv")
    has_df = pd.read_csv("has_certification.csv")

    print("Data loaded successfully.\n")


def view_employee_certifications():
    if employees_df is None or has_df is None or certifications_df is None:
        print("⚠ Please load data first (option 1).\n")
        return

    emp_id = Data_import.get_integer("Enter employee ID: ", 1, 999999)

    emp_row = employees_df[employees_df["employee_id"] == emp_id]
    if emp_row.empty:
        print("No employee found with that ID.\n")
        return

    emp_name = emp_row.iloc[0]["first_name"] + " " + emp_row.iloc[0]["last_name"]
    print(f"\nCertifications for {emp_name} (ID {emp_id}):")

    merged = has_df.merge(certifications_df,
                          left_on="certification_id",
                          right_on="certification_id",
                          how="inner")

    emp_certs = merged[merged["employee_id"] == emp_id]

    if emp_certs.empty:
        print("  – No certifications on record.\n")
    else:
        for _, row in emp_certs.iterrows():
            print(f"  - {row['name']} (obtained {row['obtained_date']}, "
                  f"expires {row['expiry_date']})")
        print()


def view_certifications_employee_has():
    if has_df is None or certifications_df is None:
        print("⚠ Please load data first (option 1).\n")
        return

    print("\nAll employee–certification records:")
    merged = has_df.merge(certifications_df,
                          on="certification_id",
                          how="left")
    print(merged.to_string(index=False))
    print()


def view_certifications_employee_needs():
    if needs_df is None or certifications_df is None:
        print(" Please load data first (option 1).\n")
        return

    print("\nEmployee certification needs:")
    merged = needs_df.merge(certifications_df,
                            on="certification_id",
                            how="left")
    print(merged.to_string(index=False))
    print()


def reminders_for_employee_certifications():
    if has_df is None or certifications_df is None:
        print(" Please load data first (option 1).\n")
        return

    from datetime import datetime, timedelta

    today = datetime.today().date()
    threshold = today + timedelta(days=30)  # expiring in next 30 days

    df = has_df.copy()
    df["expiry_date"] = pd.to_datetime(df["expiry_date"]).dt.date

    expiring = df[df["expiry_date"] <= threshold]

    if expiring.empty:
        print("No certifications expiring in the next 30 days.\n")
        return

    merged = expiring.merge(certifications_df, on="certification_id", how="left")
    print("\nCertifications expiring soon:")
    print(merged.to_string(index=False))
    print()


def send_request_for_renewal():
    # For now just simulate sending requests – you can plug in email later
    print("Sending renewal request emails (simulated)...")
    print("Requests sent.\n")


def record_employee_has_certification():
    global has_df

    if has_df is None:
        print(" Please load data first (option 1).\n")
        return

    emp_id = Data_import.get_integer("Enter employee ID: ", 1, 999999)
    cert_id = Data_import.get_integer("Enter certification ID: ", 1, 999999)
    obtained = input("Enter obtained date (YYYY-MM-DD): ")
    expiry = input("Enter expiry date (YYYY-MM-DD): ")

    new_row = {
        "employee_id": emp_id,
        "certification_id": cert_id,
        "obtained_date": obtained,
        "expiry_date": expiry,
    }
    has_df = pd.concat([has_df, pd.DataFrame([new_row])], ignore_index=True)

    print("Certification recorded for employee.\n")


def save_changes():
    # Save any changed dataframes back to disk
    if employees_df is not None:
        employees_df.to_csv("employees.csv", index=False)
    if certifications_df is not None:
        certifications_df.to_csv("certifications.csv", index=False)
    if needs_df is not None:
        needs_df.to_csv("needs_certification.csv", index=False)
    if has_df is not None:
        has_df.to_csv("has_certification.csv", index=False)

    print("Changes saved back to CSV files.\n")


def main():
    menu_text = """
We Build Stuff FIS menu
=============================

1. Read data
2. View Employee Certifications
3. View certifications employee has
4. View certifications employee needs
5. Reminders for employee certifications
6. Send request for renewal/expires
7. Record employee has certifications
8. (unused / future option)
9. Save changes
10. Exit

=============================
"""

    user_choice = 0
    while user_choice != 10:
        print(menu_text)
        user_choice = Data_import.get_integer("Enter your choice ", 1, 10)

        clear_screen()

        if user_choice == 1:
            load_data()
        elif user_choice == 2:
            view_employee_certifications()
        elif user_choice == 3:
            view_certifications_employee_has()
        elif user_choice == 4:
            view_certifications_employee_needs()
        elif user_choice == 5:
            reminders_for_employee_certifications()
        elif user_choice == 6:
            send_request_for_renewal()
        elif user_choice == 7:
            record_employee_has_certification()
        elif user_choice == 8:
            print("Option 8 not implemented yet.\n")
        elif user_choice == 9:
            save_changes()
        elif user_choice == 10:
            if input("Are you sure you want to exit? Y/N: ").upper() == "Y":
                print("Goodbye")
                break
            else:
                user_choice = 0  # go back to menu
                clear_screen()


if __name__ == "__main__":
    main()
