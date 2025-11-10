-- Employees
INSERT INTO Employee (EmployeeID, FirstName, LastName, Email, HireDate, EmploymentStatus)
VALUES
(1, 'Alex', 'Johnson', 'alex.johnson@wbs.com', '2023-01-15', 'Active'),
(2, 'Maria', 'Lopez', 'maria.lopez@wbs.com', '2022-10-01', 'Active');

-- Certifications
INSERT INTO Certification (CertificationID, CertificationName, Description, ValidityPeriodMonths, IsRequired)
VALUES
(1, 'Forklift Safety Level 1', 'Basic forklift operation and safety.', 12, 1),
(2, 'Machine Guarding', 'Safe operation around guarded machinery.', 24, 1);

-- EmployeeCertification
INSERT INTO EmployeeCertification (EmployeeCertificationID, EmployeeID, CertificationID, DateObtained, ExpirationDate, Status)
VALUES
(1, 1, 1, '2024-01-10', '2025-01-10', 'Active'),
(2, 1, 2, '2023-07-01', '2025-07-01', 'Active'),
(3, 2, 1, '2023-11-15', '2024-11-15', 'Active');

-- Reminders (example near-expiry)
INSERT INTO Reminder (ReminderID, EmployeeCertificationID, ReminderDate, ReminderType, Status, Notes)
VALUES
(1, 1, '2024-12-15', 'Email', 'Sent', '30-day reminder before expiration'),
(2, 3, '2024-10-15', 'Email', 'Sent', '30-day reminder before expiration');
