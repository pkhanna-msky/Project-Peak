import sqlite3

def create_database():
    conn = sqlite3.connect("hrs_certifications.db")
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS Employee (
        EmployeeID INTEGER PRIMARY KEY,
        FirstName TEXT,
        LastName TEXT,
        Email TEXT,
        HireDate TEXT,
        EmploymentStatus TEXT
    );

    CREATE TABLE IF NOT EXISTS Certification (
        CertificationID INTEGER PRIMARY KEY,
        CertificationName TEXT,
        Description TEXT,
        ValidityPeriodMonths INTEGER,
        IsRequired INTEGER
    );

    CREATE TABLE IF NOT EXISTS EmployeeCertification (
        EmployeeCertificationID INTEGER PRIMARY KEY,
        EmployeeID INTEGER,
        CertificationID INTEGER,
        DateObtained TEXT,
        ExpirationDate TEXT,
        Status TEXT,
        FOREIGN KEY(EmployeeID) REFERENCES Employee(EmployeeID),
        FOREIGN KEY(CertificationID) REFERENCES Certification(CertificationID)
    );

    CREATE TABLE IF NOT EXISTS Reminder (
        ReminderID INTEGER PRIMARY KEY,
        EmployeeCertificationID INTEGER,
        ReminderDate TEXT,
        ReminderType TEXT,
        Status TEXT,
        Notes TEXT,
        FOREIGN KEY(EmployeeCertificationID) REFERENCES EmployeeCertification(EmployeeCertificationID)
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Database created successfully.")
