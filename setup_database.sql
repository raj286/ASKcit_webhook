-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS student_db;
USE student_db;

-- Create students table
CREATE TABLE IF NOT EXISTS students (
    roll_number VARCHAR(20) PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    cgpa DECIMAL(3,2) NOT NULL
);

-- Create Faculty table
CREATE TABLE IF NOT EXISTS Faculty (
    faculty_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL
);

-- Sample data for testing
INSERT INTO students (roll_number, student_name, cgpa) VALUES
('2020001', 'John Doe', 3.75),
('2020002', 'Jane Smith', 3.90),
('2020003', 'Bob Johnson', 3.45);

INSERT INTO Faculty (faculty_id, name, department, email, phone) VALUES
('FAC001', 'Dr. Alice Brown', 'Computer Science', 'alice.brown@example.com', '123-456-7890'),
('FAC002', 'Dr. Robert White', 'Mathematics', 'robert.white@example.com', '234-567-8901'),
('FAC003', 'Prof. Carol Green', 'Physics', 'carol.green@example.com', '345-678-9012'); 