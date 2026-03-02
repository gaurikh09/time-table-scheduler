# University Timetable Scheduler - NEP 2020 Aligned

A production-level intelligent timetable scheduling system built with Django and Google OR-Tools.

## Features

- **Intelligent Scheduling**: Uses Google OR-Tools CP-SAT solver for optimal timetable generation
- **Clash-Free**: Prevents room, faculty, and batch conflicts
- **Fixed Allocations**: Support for locked manual entries and batch-specific room constraints
- **Role-Based Access**: Admin, Coordinator, and Reviewer roles
- **Modern UI**: Clean, responsive dashboard interface
- **NEP 2020 Compliant**: Designed for modern university requirements

## Tech Stack

- **Backend**: Django 4.2
- **Frontend**: HTML, CSS, JavaScript (Django Templates)
- **Database**: SQLite (development) - PostgreSQL ready
- **Optimization**: Google OR-Tools CP-SAT Solver

## Installation

### 1. Clone and Setup

```bash
cd university_scheduler
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Run Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## Project Structure

```
university_scheduler/
├── manage.py
├── requirements.txt
├── scheduler_project/
│   ├── settings.py          # Django configuration
│   ├── urls.py              # Main URL routing
│   └── wsgi.py
├── core/                    # Main application
│   ├── models.py            # Database models
│   ├── views.py             # View logic
│   ├── forms.py             # Form definitions
│   ├── urls.py              # App URL routing
│   └── admin.py             # Admin configuration
├── scheduler_engine/        # Scheduling logic (separate)
│   └── solver.py            # OR-Tools solver
├── templates/               # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   ├── timetable/
│   ├── academic/
│   ├── infrastructure/
│   └── forms/
└── static/                  # CSS & JavaScript
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Usage Workflow

### 1. Infrastructure Setup (Admin)
- Create Academic Blocks
- Add Floors to blocks
- Add Rooms with capacity and type

### 2. Academic Configuration (Admin/Coordinator)
- Create Departments
- Add Batches (with optional fixed room)
- Add Faculty members
- Create Subjects
- Map Faculty to Subjects and Batches

### 3. Manual Entries (Optional)
- Create fixed timetable entries
- Mark entries as "locked" to preserve during regeneration

### 4. Generate Timetable
- Click "Generate Timetable"
- System runs OR-Tools solver
- View results in timetable grid

### 5. Review & Approve (Reviewer)
- Review generated timetable
- Export to PDF if needed

## Key Features Explained

### Batch Fixed Room Constraint
Set a fixed room for a batch (e.g., 2nd Year EB → Room 7025). All classes for that batch will be scheduled in that room only.

### Locked Manual Entries
Mark specific timetable entries as "Fixed". These will be preserved during regeneration and treated as hard constraints.

### Constraint Satisfaction

**Hard Constraints:**
- No room clashes
- No faculty clashes
- No batch clashes
- Weekly subject frequency satisfied
- Max classes per day per batch
- Room capacity ≥ batch strength
- Respect batch fixed-room constraint
- Respect locked manual entries
- Working hours: 10 AM - 6 PM

**Soft Constraints (Optimization):**
- Balance faculty workload
- Minimize schedule gaps
- Maximize room utilization

## User Roles

- **Admin**: Full access to infrastructure and academic management
- **Coordinator**: Manage academic entities, generate timetables
- **Reviewer**: View and approve timetables

## Database Migration to PostgreSQL

To switch from SQLite to PostgreSQL:

1. Install psycopg2: `pip install psycopg2-binary`
2. Update `settings.py`:

```python
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

3. Run migrations: `python manage.py migrate`

## Troubleshooting

### Timetable Generation Fails
- Check if all batches have faculty-subject mappings
- Verify room capacities are sufficient
- Reduce fixed constraints if too restrictive
- Check subject weekly frequencies are realistic

### No Rooms Available
- Ensure rooms are marked as "allocatable"
- Check room capacities match batch strengths
- Verify fixed room constraints aren't conflicting

## Production Deployment

1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS`
3. Use environment variables for `SECRET_KEY`
4. Set up PostgreSQL database
5. Configure static files: `python manage.py collectstatic`
6. Use gunicorn/uwsgi for WSGI server
7. Set up nginx for reverse proxy

## License

This project is built for educational and institutional use.

## Support

For issues or questions, refer to the Django and OR-Tools documentation:
- Django: https://docs.djangoproject.com/
- OR-Tools: https://developers.google.com/optimization
