# HostelEase: Campus Hostel Management System

**Course Code**: 23CS11E / 23IT11E – Web Frameworks using Python  
**Scenario**: Team 5 – HostelEase

## Overview
HostelEase is a full-featured Django web application designed to automate hostel accommodation, room allotments, fee payments, and maintenance complaints with real-time analytics.

---

## 👥 Module Distribution

| Member | Module | Key Features |
|---|---|---|
| **Member 1** | Room Allotment & Vacancy Tracking | Room & block catalog, bed capacity calculation, student application form, warden allotment/vacate approval |
| **Member 2** | Fee Payment Integration | Semester fee ledger, mock payment gateway flow, transaction logging, printable receipts |
| **Member 3** | Complaint Management & Analytics | Maintenance ticketing with photo proof, status lifecycle (`Pending` ➔ `In-Progress` ➔ `Resolved`), Chart.js visual dashboard, CSV reports |

---

## 🛠 Tech Stack
- **Backend**: Python 3, Django
- **Database**: SQLite
- **Frontend**: HTML5, Bootstrap 5, Bootstrap Icons, Chart.js
- **Media**: Django Media Handling & Pillow

---

## 🚀 Setup & Run Locally

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Load Sample Data**:
   ```bash
   python seed_data.py
   ```

4. **Start Development Server**:
   ```bash
   python manage.py runserver
   ```
   Open your browser and navigate to: `http://127.0.0.1:8000/`

---

## 🔑 Demo Credentials

| Role | Username | Password |
|---|---|---|
| **Warden / Admin** | `warden` | `admin123` |
| **Student** | `student1` | `student123` |
