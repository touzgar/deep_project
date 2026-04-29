# Bugfix Requirements Document

## Introduction

The Smart Face Attendance System's dashboard and attendance pages are displaying incomplete data due to backend API endpoints returning partial data structures. The dashboard stats API (`/dashboard/stats`) is missing critical chart data arrays (weeklyAttendance, monthlyAttendanceRate, presentVsAbsent) and today's session metrics (totalSessionsToday, presentToday, absentToday, attendancePercentage). Additionally, the attendance records API does not include student names, forcing the frontend to display student IDs instead of readable names.

This bugfix ensures all API endpoints return complete data structures with real database-derived values, eliminating the need for any hardcoded or mock data in the frontend.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN the frontend requests `/dashboard/stats` THEN the system returns only basic counts (`total_students`, `total_classes`, `total_sessions`, `total_attendance`) without chart data arrays

1.2 WHEN the frontend requests `/dashboard/stats` THEN the system does not include `weeklyAttendance`, `monthlyAttendanceRate`, or `presentVsAbsent` arrays needed for dashboard charts

1.3 WHEN the frontend requests `/dashboard/stats` THEN the system does not include today's metrics (`totalSessionsToday`, `presentToday`, `absentToday`, `attendancePercentage`)

1.4 WHEN the frontend requests `/attendance/` THEN the system returns attendance records with only `student_id` (integer foreign key) without the associated student's name

1.5 WHEN the frontend displays attendance records THEN the system shows "Student ID: 123" instead of "John Doe" because student names are not included in the API response

### Expected Behavior (Correct)

2.1 WHEN the frontend requests `/dashboard/stats` THEN the system SHALL return a complete stats object including `totalStudents`, `totalClasses`, `totalSessionsToday`, `presentToday`, `absentToday`, `attendancePercentage`, `weeklyAttendance`, `monthlyAttendanceRate`, and `presentVsAbsent` arrays

2.2 WHEN the frontend requests `/dashboard/stats` THEN the system SHALL calculate `weeklyAttendance` as an array of 7 objects with format `{name: "Mon", present: X, absent: Y}` based on the last 7 days of attendance data from the database

2.3 WHEN the frontend requests `/dashboard/stats` THEN the system SHALL calculate `monthlyAttendanceRate` as an array of objects with format `{name: "Week 1", rate: X}` showing attendance percentage for the last 4 weeks from the database

2.4 WHEN the frontend requests `/dashboard/stats` THEN the system SHALL calculate `presentVsAbsent` as an array with format `[{name: "Present", value: X}, {name: "Absent", value: Y}]` based on today's attendance logs

2.5 WHEN the frontend requests `/dashboard/stats` THEN the system SHALL calculate today's metrics by querying sessions and attendance logs for the current date

2.6 WHEN the frontend requests `/attendance/` THEN the system SHALL return attendance records with a `student_name` field containing the full name (first_name + last_name) by joining with the students table

2.7 WHEN the frontend displays attendance records THEN the system SHALL show readable student names like "John Doe" instead of numeric IDs

### Unchanged Behavior (Regression Prevention)

3.1 WHEN the frontend requests `/students/` THEN the system SHALL CONTINUE TO return the complete list of students with all existing fields

3.2 WHEN the frontend requests `/classes/` THEN the system SHALL CONTINUE TO return the complete list of classes with all existing fields

3.3 WHEN the frontend requests `/sessions/` THEN the system SHALL CONTINUE TO return the complete list of sessions with all existing fields

3.4 WHEN the frontend creates a new attendance record via POST `/attendance/` THEN the system SHALL CONTINUE TO save it to the database successfully

3.5 WHEN the frontend requests `/attendance/export` THEN the system SHALL CONTINUE TO generate and return a CSV file with attendance data

3.6 WHEN authentication endpoints (`/auth/login`, `/auth/signup`, `/auth/me`) are called THEN the system SHALL CONTINUE TO function correctly with JWT token validation

3.7 WHEN the live camera AI module detects a face and creates attendance records THEN the system SHALL CONTINUE TO save them to the database correctly
