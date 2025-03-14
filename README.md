# AskCIT Webhook

A Flask-based webhook for handling Dialogflow intents for a college information system.

## Features

- **Student CGPA Lookup**: Retrieve student CGPA by roll number
- **Faculty Information**: Get detailed information about faculty members by ID or name
- **Department Faculty**: List all faculty members in a specific department

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up MySQL database with the required tables:
   - students (roll_number, student_name, cgpa)
   - faculty (faculty_id, faculty_name, department, roles, qualification, email)

4. Run the application:
   ```
   python askcit.py
   ```

## Dialogflow Integration

This webhook is designed to work with Dialogflow intents:
- grade_cgpa1: For student CGPA queries
- Facultyinfo: For faculty information queries
- DepartmentFaculty: For listing faculty by department

## Environment Variables

You can configure the database connection using environment variables:
- DB_HOST: Database host (default: localhost)
- DB_USER: Database user (default: root)
- DB_PASSWORD: Database password
- DB_NAME: Database name (default: student_db) 