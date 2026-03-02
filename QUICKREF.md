# Quick Reference - University Timetable Scheduler

## Essential Commands

### Initial Setup
```bash
# Navigate to project
cd university_scheduler

# Install dependencies
pip install -r requirements.txt

# Create database tables
python manage.py makemigrations
python manage.py migrate

# Load sample data (includes admin user)
python manage.py init_sample_data

# Start server
python manage.py runserver
```

### Access Application
- URL: http://127.0.0.1:8000
- Admin: username=`admin`, password=`admin123`
- Coordinator: username=`coordinator`, password=`coord123`

### Create Custom Superuser
```bash
python manage.py createsuperuser
```

### Django Admin Panel
- URL: http://127.0.0.1:8000/admin
- Full database access and management

## Application URLs

| Feature | URL |
|---------|-----|
| Dashboard | `/` |
| Login | `/login/` |
| Logout | `/logout/` |
| Blocks | `/blocks/` |
| Rooms | `/rooms/` |
| Departments | `/departments/` |
| Batches | `/batches/` |
| Faculty | `/faculty/` |
| Subjects | `/subjects/` |
| Mappings | `/faculty-subjects/` |
| Generate | `/timetable/generate/` |
| View Timetable | `/timetable/view/` |
| Manual Entry | `/timetable/manual-entry/` |

## Key Concepts

### Fixed Room Constraint
When creating/editing a batch, set `fixed_room` field to lock all classes to that room.

Example: Batch "2nd Year EB" → Room 7025

### Locked Manual Entries
When creating manual timetable entries, check `is_fixed` to preserve during regeneration.

### Working Hours
Default: 10 AM - 6 PM (configurable in settings.py)

### Timeslots
1-hour slots by default (configurable)

## Workflow Summary

1. **Infrastructure** (Admin only)
   - Create Block → Add Floors → Add Rooms

2. **Academic Setup** (Admin/Coordinator)
   - Create Department
   - Add Batches (optionally set fixed room)
   - Add Faculty
   - Create Subjects
   - Map Faculty-Subject-Batch

3. **Generate Timetable** (Admin/Coordinator)
   - Navigate to "Generate Timetable"
   - Click generate button
   - Wait for completion

4. **View Results** (All roles)
   - Select batch from dropdown
   - View weekly timetable grid

## Troubleshooting Quick Fixes

### Import Error
```bash
pip install --upgrade Django ortools
```

### Database Issues
```bash
# Reset database (WARNING: deletes all data)
del db.sqlite3
python manage.py migrate
python manage.py init_sample_data
```

### Static Files Not Loading
Check `settings.py`:
- DEBUG = True
- STATIC_URL = 'static/'

### Generation Fails
- Verify faculty-subject mappings exist
- Check room capacities ≥ batch strengths
- Reduce fixed constraints

## File Locations

| Component | File Path |
|-----------|-----------|
| Models | `core/models.py` |
| Views | `core/views.py` |
| Forms | `core/forms.py` |
| URLs | `core/urls.py` |
| Solver | `scheduler_engine/solver.py` |
| Settings | `scheduler_project/settings.py` |
| CSS | `static/css/style.css` |
| JavaScript | `static/js/main.js` |

## Sample Data Included

After running `init_sample_data`:
- 2 Users (admin, coordinator)
- 1 Block (AB - Academic Block A)
- 1 Floor (Floor 7)
- 3 Rooms (7025, 7026, 7027)
- 2 Departments (CSE, ECE)
- 2 Batches (CSE 2nd Year EB with fixed room, EA without)
- 2 Faculty members
- 3 Subjects (Data Structures, Algorithms, DBMS)
- 3 Faculty-Subject mappings

## Production Deployment Checklist

- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use PostgreSQL database
- [ ] Set `SECRET_KEY` from environment
- [ ] Run `collectstatic`
- [ ] Use gunicorn/uwsgi
- [ ] Configure nginx
- [ ] Enable HTTPS
- [ ] Set up backups
- [ ] Configure logging

## Support Resources

- Django Docs: https://docs.djangoproject.com/
- OR-Tools Docs: https://developers.google.com/optimization
- Project Docs: See DOCUMENTATION.md
- Setup Guide: See SETUP.md
