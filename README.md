# University Timetable Scheduler

A full-featured intelligent timetable scheduling system built with Django and Google OR-Tools CP-SAT solver. Supports multi-role access, combined classes, student portals, class advisor management, and automatic conflict detection.

---

## Features

- **AI-Powered Scheduling** — Google OR-Tools CP-SAT solver generates clash-free timetables automatically
- **Combined Classes** — Schedule a single slot shared across multiple batches with one faculty
- **Lab / Multi-Hour Support** — 2-hour lab subjects merge into a single block in the timetable grid
- **Saved Timetables** — Previous timetable is automatically snapshotted before every regeneration
- **Role-Based Access** — Admin, Coordinator, Class Advisor, Student roles with fine-grained permissions
- **Class Advisor Portal** — Faculty assigned as class advisors manage their own batch's timetable
- **Student Portal** — Students log in and view only their batch's timetable
- **Student Management** — Add students individually or via CSV upload
- **Detailed Error Diagnostics** — On generation failure, specific reasons are shown (room capacity, frequency overflow, etc.)
- **Modern Dark UI** — Responsive sidebar layout with auto-dismiss alerts and logout dropdown

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2.7 |
| Solver | Google OR-Tools CP-SAT |
| Database | SQLite (dev) / PostgreSQL-ready |
| Frontend | Django Templates, HTML, CSS, JS |
| Auth | Django built-in auth with custom User model |

---

## Installation

### 1. Clone and enter the project

```bash
git clone https://github.com/gaurikh09/time-table-scheduler.git
cd time-table-scheduler/university_scheduler
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` contains:
```
Django==4.2.7
ortools==9.8.3296
```

### 3. Apply migrations

```bash
python manage.py migrate
```

### 4. Create an admin superuser

```bash
python manage.py createsuperuser
```

Then set the role to `admin` via the Django shell or the `set_admin_role.py` script:

```bash
python set_admin_role.py
```

### 5. Run the development server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

---

## Project Structure

```
university_scheduler/
├── manage.py
├── requirements.txt
├── scheduler_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                          # Main application
│   ├── models.py                  # All database models
│   ├── views.py                   # All view logic
│   ├── forms.py                   # Form definitions
│   ├── urls.py                    # URL routing
│   ├── admin.py
│   └── templatetags/
│       └── custom_filters.py      # get_item, entry_rowspan, split_csv
├── scheduler_engine/
│   └── solver.py                  # OR-Tools CP-SAT timetable solver
├── templates/
│   ├── base.html                  # Sidebar layout, logout, alerts
│   ├── dashboard.html
│   ├── login.html
│   ├── landing.html
│   ├── academic/                  # Batch, faculty, subject, department templates
│   ├── infrastructure/            # Block, room templates
│   ├── timetable/                 # Generate, view, saved, combined class templates
│   ├── forms/                     # CSV upload and form templates
│   ├── advisor/                   # Class advisor management templates
│   └── students/                  # Student management and student timetable
└── static/
    ├── css/dashboard.css
    └── js/dashboard.js
```

---

## Data Models

| Model | Description |
|---|---|
| `User` | Custom user with roles: admin, coordinator, reviewer, class_advisor, student |
| `AcademicBlock` | Building block (e.g. Block A) |
| `Floor` | Floor within a block |
| `Room` | Room with capacity, type, allocatable flag |
| `Department` | Academic department |
| `Batch` | Year/Semester/Section group of students |
| `Faculty` | Teaching staff |
| `Subject` | Course with type, weekly frequency, duration |
| `BatchSubject` | Subject assigned to a batch (via CSV) |
| `FacultySubject` | Faculty assigned to teach a subject for a batch |
| `TimetableEntry` | A single scheduled class slot |
| `CombinedClass` | A slot shared by multiple batches |
| `ClassAdvisor` | Links a User (class_advisor role) to a Faculty and Batch |
| `Student` | Links a User (student role) to a Batch |
| `SavedTimetable` | Snapshot of a timetable before regeneration |
| `SavedTimetableEntry` | Denormalized entry in a saved snapshot |
| `TimetableGeneration` | Log of each generation attempt |

---

## User Roles & Permissions

### Admin
- Full access to everything
- Manage infrastructure (blocks, floors, rooms)
- Create and manage Class Advisor accounts (generate login credentials)
- View and manage all batches, students, timetables

### Coordinator
- Manage academic data (departments, batches, faculty, subjects, mappings)
- Generate and view timetables
- Upload CSVs

### Class Advisor
- Assigned to one batch by admin
- Can add/edit faculty and subjects
- Upload faculty, subject, and mapping CSVs
- Generate timetable **only for their assigned batch**
- Manage combined classes (can select all batches to combine)
- Add/upload students for their batch
- View their batch's timetable

### Student
- Logs in and is redirected directly to their batch's timetable
- Read-only timetable view with print support
- Cannot access any management sections

---

## Usage Workflow

### Step 1 — Infrastructure (Admin)
1. Create **Academic Blocks**
2. Add **Floors** to each block
3. Add **Rooms** with capacity and type

### Step 2 — Academic Setup (Admin / Coordinator / Class Advisor)
1. Create **Departments**
2. Create **Batches** (department, year, semester, section, strength)
3. Add **Faculty** members (manually or via CSV)
4. Create **Subjects** (manually or via CSV)
5. Assign subjects to batches via **Batch-Subject CSV**
6. Assign faculty to subjects per batch via **Faculty-Subject Mappings**

### Step 3 — Combined Classes (Optional)
- Go to **Combined Classes** → Add Combined Class
- Select day, time, subject, faculty, room, and multiple batches
- Combined classes are pre-placed before solver runs and are not re-scheduled

### Step 4 — Generate Timetable
- Go to **Generate Timetable**
- Select a batch (class advisors see only their batch)
- Click Generate — OR-Tools solver runs
- If it fails, specific diagnostic reasons are shown
- Previous timetable is automatically saved as a snapshot

### Step 5 — View & Print
- Go to **View Timetable** → select batch
- Lab/2-hour subjects span two rows automatically
- Combined classes shown with dashed purple border and batch section chips
- Print button available

### Step 6 — Student Access
- Admin or Class Advisor goes to **Student Management**
- Add students individually or upload CSV (`username, password, full_name, roll_number`)
- Students log in at `/login/` and are redirected to their timetable automatically

---

## Timetable Solver Constraints

### Hard Constraints
- No room clashes (same room, same time)
- No faculty clashes (same faculty, same time)
- No batch clashes (same batch, same time)
- Weekly subject frequency exactly satisfied
- Max classes per day per batch respected
- Room capacity ≥ batch strength
- Batch fixed-room constraint respected
- Locked manual entries preserved
- Combined class slots pre-blocked (not re-scheduled)
- Subjects already in combined classes excluded from solver
- Working hours: 10:00 AM – 6:00 PM
- Lunch break: 1:00 PM – 2:00 PM (no class crosses this)

### Diagnostic Messages on Failure
When generation fails, the system reports specific issues:
- No rooms with sufficient capacity
- Total weekly hours exceed available slots
- `max_classes_per_day` too low
- Subject frequency exceeds working days
- Lab subject has insufficient valid 2-hour slots
- Faculty blocked by combined classes on all days

---

## CSV Upload Formats

### Faculty CSV
```
Teach-name, Emp-ID, email
Dr. Sharma, EMP001, sharma@uni.edu
```

### Subject CSV
```
subject-code, subject-name, weekly-frequency
CS101, Data Structures, 3
```

### Batch-Subject CSV
```
section, subject-code1, subject-code2, ...
A, CS101, CS102, CS103
```

### Faculty-Subject Mapping CSV
```
faculty_emp_id, subject_code, batch_section
EMP001, CS101, A
```

### Student CSV
```
username, password, full_name, roll_number
aryan2021, pass123, Aryan Gupta, 2021CSE001
```

---

## Switching to PostgreSQL

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'timetable_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

```bash
pip install psycopg2-binary
python manage.py migrate
```

---

## Production Deployment

```bash
# 1. Set environment variables
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

# 2. Collect static files
python manage.py collectstatic

# 3. Run with gunicorn
gunicorn scheduler_project.wsgi:application --bind 0.0.0.0:8000

# 4. Set up nginx as reverse proxy
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Generation fails — INFEASIBLE | Check the diagnostic bullet points shown on the page |
| No rooms available | Ensure rooms are marked allocatable and capacity ≥ batch strength |
| Class advisor sees all batches in generate | Verify ClassAdvisor record is linked to the user |
| Student redirected to error page | Ensure a Student record is linked to the user's account |
| TemplateSyntaxError on saved timetable | Ensure `{% load custom_filters %}` is at top of template |

---

## License

Built for educational and institutional use.

## References

- Django: https://docs.djangoproject.com/
- OR-Tools: https://developers.google.com/optimization
- OR-Tools CP-SAT: https://developers.google.com/optimization/reference/python/sat/python/cp_model
