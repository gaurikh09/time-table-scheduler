# Quick Setup Guide

## Step-by-Step Setup

### 1. Navigate to project directory
```bash
cd university_scheduler
```

### 2. Create virtual environment (optional but recommended)
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Initialize sample data (optional)
```bash
python manage.py init_sample_data
```

This creates:
- Admin user: username=`admin`, password=`admin123`
- Coordinator user: username=`coordinator`, password=`coord123`
- Sample departments, batches, faculty, subjects
- Sample rooms with Room 7025 fixed to Batch EB

### 6. Start development server
```bash
python manage.py runserver
```

### 7. Access the application
Open browser: http://127.0.0.1:8000

Login with admin credentials to access all features.

## Manual Setup (without sample data)

If you skip step 5, create a superuser manually:
```bash
python manage.py createsuperuser
```

Then configure:
1. Infrastructure (Blocks → Floors → Rooms)
2. Departments
3. Batches (optionally set fixed room)
4. Faculty
5. Subjects
6. Faculty-Subject mappings
7. Generate timetable

## Key Features to Test

1. **Fixed Room Constraint**: Create a batch with fixed_room set to test batch-level room locking
2. **Manual Locked Entries**: Create manual timetable entries with is_fixed=True
3. **Timetable Generation**: Navigate to "Generate Timetable" and run the solver
4. **View Timetable**: Select a batch to view the generated schedule

## Troubleshooting

**Import Error for ortools**: 
```bash
pip install --upgrade ortools
```

**Database locked error**:
Close any DB browser tools and restart server

**Static files not loading**:
Ensure DEBUG=True in settings.py for development

## Production Checklist

- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set strong SECRET_KEY from environment variable
- [ ] Run collectstatic
- [ ] Use gunicorn/uwsgi
- [ ] Set up nginx reverse proxy
- [ ] Enable HTTPS
