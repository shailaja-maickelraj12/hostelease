# HostelEase: Campus Hostel Management System
## Member 1 Module: Room Allotment & Vacancy Tracking

**Course**: 23CS11E / 23IT11E – Web Frameworks using Python  
**Scenario**: Team 5 – HostelEase  
**Module Assigned**: **Member 1 – Room Allotment & Vacancy Tracking**

---

### 📌 Module Scope & Features
1. **User Authentication & Role Management**:
   - Secure Student registration and Login/Logout.
   - Dual roles: Student and Warden/Admin with permission safeguards.
   - Role-specific dashboard redirection.

2. **Room & Block Inventory**:
   - Boys and Girls hostel block cataloging with floor structures.
   - Multiple room configurations: Single AC, Double Non-AC, Triple Non-AC.
   - Live vacancy tracking (`capacity - occupied_beds`) and capacity check indicators.

3. **Room Allotment Workflow**:
   - Interactive room catalog where students filter by block and room type.
   - Student submits room allocation request.
   - Warden approves, rejects, or marks room as vacated.
   - Real-time automatic increment/decrement of vacant bed counter.

4. **Reporting**:
   - CSV export of student room allocations and occupancy data for hostel administration.

---

### 🛠 Tech Stack
- **Framework**: Django (Python)
- **Database**: SQLite
- **Frontend**: HTML5, Bootstrap 5, Bootstrap Icons

---

### 🚀 Setup & Execution

1. **Install Dependencies**:
   ```bash
   pip install django
   ```

2. **Run Migrations**:
   ```bash
   python manage.py makemigrations
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
   Open `http://127.0.0.1:8000/` in your browser.

---

### 🔑 Demo Credentials
- **Warden**: `warden` / `admin123`
- **Student**: `student1` / `student123`
