sudo apt install sqlite3

sqlite:///mydatabase.db

Assumptions

for staff member to shift swap 
	1. They have to be in same roster
	2. User can't swap with other user if the other user don't have shift for that day
	3. User can directly swap with member without anyone permissions

Marking attendance api 
	1. We don't have to mark both checkin and checkout time

	potential solution to make this api better
	# Attendance Management System with Image Capture

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Technologies Used](#technologies-used)
4. [Installation](#installation)
5. [Usage](#usage)
6. [API Endpoints](#api-endpoints)
7. [Assumptions](#assumptions)
8. [Potential Solutions to Improve the Attendance API](#potential-solutions-to-improve-the-attendance-api)
9. [Future Enhancements](#future-enhancements)
10. [License](#license)

---

## Overview

The **Attendance Management System with Image Capture** is a web application designed to streamline attendance tracking and roster management in workplaces. It features role-based authentication, roster creation by managers, and attendance marking with image capture by staff. This ensures an efficient and tamper-proof way to manage staff attendance.

---

## Features

### Authentication & Authorization
- **Roles:** Manager, Staff, ADMIN.
- Managers can:
  - Create, view, and edit rosters.
  - Add new staff members.
  - Set working days, shifts, and weekly offs.
- Staff can:
  - View their assigned shifts.
  - Mark attendance via webcam within an hour of their shift timings.
- Admin can:
	- Create Manager user 
	- Same permission as Manager

### Roster Management
- Managers:
  - Add and manage staff details.
  - Set unique shifts for different days of the week.
  - Assign 1-2 weekly offs for each staff member.
  - View and update the complete roster.
- Staff:
  - Request shift interchange with other staff members.

### Attendance Management
- Staff members:
  - Mark attendance by capturing an image using a webcam.
  - Attendance is timestamped and linked with the captured image.
- System ensures:
  - Attendance is marked only within 1 hour of shift timings.

---

## Technologies Used

### Backend
- **Programming Language:** Python
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **Authentication:** JWT-based token authentication

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-repo/attendance-management-system.git
   cd attendance-management-system
