import os
import pandas as pd

def read_data():
    subfolder_path = "data"
    certifications = pd.read_csv(os.path.join(subfolder_path, "certifications.csv"))
    certifications.set_index('CertificationsID', inplace=True)
    employees= pd.read_csv(os.path.join(subfolder_path, "emplopyees.csv"))
    employees.set_index('PO_ID', inplace=True)
    has_certifications = pd.read_csv(os.path.join(subfolder_path, "has_certifications.csv"))
    has_certifications.set_index('certificationsID', inplace=True)
    needs_certifications = pd.read_csv(os.path.join(subfolder_path, "needs_certifications.csv"))
    needs_certifications.set_index('certificationsID', inplace=True)
    reminder = pd.read_csv(os.path.join(subfolder_path, "reminder.csv"))
    reminder.set_index('certificationsID', inplace=True)
    input("Press enter to continue...") 
    input("Press enter to continue...") 
    return certifications, employees, has_certifications, needs_certifications, reminder
#