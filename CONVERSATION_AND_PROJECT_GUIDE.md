# HostelEase: Campus Hostel Management System
## Complete Project Discussion, Architecture & Collaboration Guide

**Course Code**: 23CS11E / 23IT11E – Web Frameworks using Python  
**Team**: Team 5 – HostelEase: Campus Hostel Management System  
**Document Path**: `C:\24205053\hostelease\CONVERSATION_AND_PROJECT_GUIDE.md`  
**GitHub Repository**: `https://github.com/shailaja-maickelraj12/hostelease`

---

## 📋 1. Project Overview & Problem Statement

### Problem Statement
On many college campuses, hostel accommodations, room allocations, fee payments, and maintenance requests are handled manually with registers and paper forms. This causes long wait times, errors in tracking room occupancy, delays in resolving student complaints, and lack of financial clarity.

### Solution
**HostelEase** is a centralized Django-based web platform designed for:
- Students to browse available rooms, submit room allotment requests, pay hostel fees online, and lodge maintenance complaints with photo proof.
- Hostel Wardens and Administrators to allocate rooms, monitor vacancies, track payments, assign technicians for repairs, and inspect real-time visual analytics.

### Suggested Tech Stack
- **Backend Framework**: Python 3.13, Django 6.1
- **Database**: SQLite (built-in) / PostgreSQL
- **Frontend**: HTML5, CSS3, Bootstrap 5, Bootstrap Icons
- **Data Visualization**: Chart.js
- **Media Handling**: Django Media & Pillow (for complaint image uploads)
- **Version Control**: Git & GitHub

---

## 👥 2. Module Distribution (As Per Syllabus PDF)

The official syllabus assigns **3 core modules** for Team 5:

| Member | Official Module Name | Key Functional Scope |
| :--- | :--- | :--- |
| **Member 1** | **Room Allotment & Vacancy Tracking** | User auth (Student & Warden), Room and Block models, real-time bed vacancy calculation, student room application workflow, warden approval and vacate actions, CSV export. |
| **Member 2** | **Fee Payment Integration** | Fee structure (Rent, Mess, Caution Deposit), student fee ledger, simulated online payment gateway (UPI/Card), transaction ID generation, printable fee receipts. |
| **Member 3** | **Complaint Management & Analytics** | Maintenance ticketing system with category and image upload, status lifecycle (`Pending` ➔ `In-Progress` ➔ `Resolved`), warden resolution notes, student rating (1-5 stars), Chart.js visual charts, CSV export. |

---

## 👥 3. Expanded 5-Member Team Allocation

For teams with **5 members**, the syllabus scope is cleanly distributed without overlap:

1. **Member 1: Authentication & Student Room Application Portal**
   - User registration & login with role checks.
   - Student dashboard & profile management.
   - Room browsing & room application form submission.

2. **Member 2: Room Inventory & Warden Allotment Management**
   - Hostel block & room master setup.
   - Real-time vacancy algorithm (`available_beds = capacity - occupied_beds`).
   - Warden allotment approval, rejection, and vacate controls.

3. **Member 3: Fee Structure & Online Payment Gateway**
   - Fee models, student fee ledger with dues and settled amounts.
   - Payment checkout simulation (UPI / Card / NetBanking) with transaction tracking.
   - Printable / downloadable electronic fee receipts.

4. **Member 4: Maintenance Grievance & Ticket Lifecycle**
   - Complaint submission form with problem category and photo proof.
   - Live ticket status tracking for students.
   - Warden staff assignment and resolution updates.
   - Student post-resolution rating and feedback.

5. **Member 5: Analytics Dashboard & Report Generation**
   - Chart.js interactive visualizations (Occupancy by Block, Fee Collection Breakdown, Issues by Category).
   - CSV export utilities for student allotments and complaints reports.
   - Advanced search and filtering queries using Django ORM.

---

## 🛠 4. Code Implemented for Member 1 (Currently Live on `main`)

### A. Database Models (`hostel/models.py`)
- **`UserProfile`**: Extends Django `User` with `role` (`student`, `warden`), `roll_number`, `phone_number`, `gender`, `department`, `guardian_name`, `guardian_phone`.
- **`HostelBlock`**: `name`, `block_type` (Boys/Girls), `total_floors`, `description`.
- **`Room`**: `block` (FK), `room_number`, `floor`, `room_type` (Single AC, Double Non-AC, Triple Non-AC), `capacity`, `occupied_beds`, `rent_per_semester`.
  - Properties: `available_beds` (`max(0, capacity - occupied_beds)`), `is_full` (`occupied_beds >= capacity`).
- **`RoomAllotment`**: `student` (FK), `room` (FK), `applied_date`, `allotment_date`, `status` (`Pending`, `Approved`, `Rejected`, `Vacated`), `remarks`.

### B. Core Views (`hostel/views.py`)
- `home`: Public landing page with live occupancy counter.
- `register_student`: Student account registration.
- `user_login` / `user_logout`: Role-based authentication and redirection.
- `student_dashboard`: Shows active allotment or pending application status.
- `warden_dashboard`: Overview of total rooms, occupied beds, vacancy rate, and pending applications.
- `room_list`: Interactive room catalog with Block and Room Type filters.
- `apply_room`: Submits student room application with validation preventing full rooms or duplicate applications.
- `my_room`: Displays student's room details and list of roommates.
- `manage_allotments`: Warden interface to approve, reject, or vacate rooms.
- `export_allotments_csv`: Exports allotment data to a downloadable CSV spreadsheet.

---

## 💻 5. Exact Code for Member 2 & Member 3 to Add

### 💳 For Member 2: Fee Payment Integration
1. **Model** to add in `hostel/models.py`:
   - `FeePayment`: fields `student`, `fee_type`, `amount`, `due_date`, `status` (`Pending`, `Paid`), `transaction_id`, `payment_method`, `paid_at`.
2. **Form** to add in `hostel/forms.py`:
   - `PaymentCheckoutForm`: fields `payment_method`, `upi_id`, `card_number`, `expiry`, `cvv`.
3. **Views** to add in `hostel/views.py`:
   - `student_fees`: view outstanding dues and settled payments.
   - `pay_fee`: checkout form that generates a unique `TXN-XXXXXXXXXX` ID and marks fee as `Paid`.
   - `fee_receipt`: printable electronic receipt layout.
   - `warden_fee_tracker`: warden ledger with status filters (Paid vs Pending defaulters).
4. **Templates** in `hostel/templates/hostel/`:
   - `student_fees.html`, `pay_fee.html`, `fee_receipt.html`, `warden_fees.html`.

### 🛠 For Member 3: Complaint Management & Analytics
1. **Model** to add in `hostel/models.py`:
   - `Complaint`: fields `student`, `room`, `category` (Electrical, Plumbing, Carpenter, Wi-Fi, Cleanliness), `title`, `description`, `image`, `status` (`Pending`, `In-Progress`, `Resolved`), `assigned_to`, `warden_remarks`, `rating`, `feedback`.
2. **Forms** to add in `hostel/forms.py`:
   - `ComplaintForm` (with image upload), `ComplaintStatusUpdateForm`, `ComplaintFeedbackForm`.
3. **Views** to add in `hostel/views.py`:
   - `complaint_list`: student views their filed tickets.
   - `submit_complaint`: student reports an issue with photo evidence.
   - `complaint_feedback`: student rates resolution (1 to 5 stars).
   - `manage_complaints`: warden reviews tickets and assigns staff.
   - `update_complaint`: warden marks tickets as Resolved.
   - `analytics_dashboard`: Chart.js visual charts (Occupancy by Block, Complaints by Category).
   - `export_complaints_csv`: CSV export for grievances.
4. **Templates** in `hostel/templates/hostel/`:
   - `complaint_list.html`, `submit_complaint.html`, `complaint_feedback.html`, `manage_complaints.html`, `update_complaint.html`, `analytics.html`.

---

## 🚀 6. Complete Git Collaboration Commands

### For Member 1 (Project Lead)
```powershell
cd C:\24205053\hostelease
git branch -M main
git remote add origin https://github.com/shailaja-maickelraj12/hostelease.git
git push -u origin main
```

### For Member 2 (Fee Payment)
```powershell
# Clone repo
git clone https://github.com/shailaja-maickelraj12/hostelease.git
cd hostelease

# Create feature branch
git checkout -b member-2-fee-payment

# (Add Member 2 code files)

# Run database migrations
python manage.py makemigrations
python manage.py migrate

# Commit and push
git add .
git commit -m "Member 2: Fee Payment Integration and Receipts"
git push -u origin member-2-fee-payment
```

### For Member 3 (Complaints & Analytics)
```powershell
# Clone repo
git clone https://github.com/shailaja-maickelraj12/hostelease.git
cd hostelease

# Create feature branch
git checkout -b member-3-complaints-analytics

# (Add Member 3 code files)

# Run database migrations
python manage.py makemigrations
python manage.py migrate

# Commit and push
git add .
git commit -m "Member 3: Complaint Management, Chart.js Analytics & Reports"
git push -u origin member-3-complaints-analytics
```

### How Member 1 Pulls and Merges Everything into `main`
```powershell
cd C:\24205053\hostelease

# 1. Fetch remote updates
git fetch origin

# 2. Merge Member 2
git checkout main
git merge origin/member-2-fee-payment

# 3. Merge Member 3
git merge origin/member-3-complaints-analytics

# 4. Run any new migrations
python manage.py makemigrations
python manage.py migrate

# 5. Push full combined project to GitHub main
git push origin main
```

---

## 🔑 7. Running and Testing the Project Locally

```powershell
cd C:\24205053\hostelease
python manage.py runserver
```

Open browser at: **`http://127.0.0.1:8000/`**

### Pre-Configured Test Accounts

| Role | Username | Password |
| :--- | :--- | :--- |
| **Hostel Warden / Administrator** | `warden` | `admin123` |
| **Student** | `student1` | `student123` |

---

## 💾 8. Local Backup Notice
A complete, pre-built backup containing **all three modules integrated together** is preserved locally on disk at:  
📁 **`C:\24205053\hostelease_all_modules_backup`**
