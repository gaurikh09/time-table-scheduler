# University Timetable Scheduler - Complete Documentation

## 🎯 Project Overview

A production-ready intelligent timetable scheduling system built with Django and Google OR-Tools CP-SAT solver, aligned with NEP 2020 requirements.

## 📁 Project Structure

```
university_scheduler/
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── README.md                          # Project documentation
├── SETUP.md                          # Quick setup guide
├── db.sqlite3                        # SQLite database (created after migration)
│
├── scheduler_project/                # Main project configuration
│   ├── __init__.py
│   ├── settings.py                   # Django settings
│   ├── urls.py                       # Root URL configuration
│   ├── wsgi.py                       # WSGI configuration
│   └── asgi.py
│
├── core/                             # Main application
│   ├── __init__.py
│   ├── models.py                     # Database models (User, Infrastructure, Academic, Timetable)
│   ├── views.py                      # View functions with role-based access
│   ├── forms.py                      # Django forms for CRUD operations
│   ├── urls.py                       # App URL routing
│   ├── admin.py                      # Django admin configuration
│   ├── apps.py
│   ├── tests.py
│   ├── templatetags/                 # Custom template filters
│   │   ├── __init__.py
│   │   └── custom_filters.py        # Dictionary access filter for templates
│   └── management/                   # Custom management commands
│       ├── __init__.py
│       └── commands/
│           ├── __init__.py
│           └── init_sample_data.py  # Sample data initialization
│
├── scheduler_engine/                 # Scheduling logic (separate from Django)
│   ├── __init__.py
│   └── solver.py                     # OR-Tools CP-SAT solver implementation
│
├── templates/                        # HTML templates
│   ├── base.html                     # Base template with sidebar layout
│   ├── dashboard.html                # Main dashboard
│   ├── login.html                    # Login page
│   ├── confirm_delete.html           # Delete confirmation
│   ├── timetable_view.html           # Timetable grid display
│   ├── timetable/
│   │   └── generate.html             # Timetable generation page
│   ├── infrastructure/
│   │   ├── block_list.html
│   │   └── room_list.html
│   ├── academic/
│   │   ├── department_list.html
│   │   ├── batch_list.html
│   │   ├── faculty_list.html
│   │   ├── subject_list.html
│   │   └── faculty_subject_list.html
│   └── forms/                        # Form templates
│       ├── batch_form.html
│       ├── block_form.html
│       ├── room_form.html
│       ├── department_form.html
│       ├── faculty_form.html
│       ├── subject_form.html
│       ├── faculty_subject_form.html
│       └── timetable_entry_form.html
│
└── static/                           # Static files
    ├── css/
    │   └── style.css                 # Complete styling with modern design
    └── js/
        └── main.js                   # JavaScript for interactions
```

## 🔑 Key Features

### 1. Role-Based Authentication
- **Admin**: Full system access
- **Coordinator**: Academic management, timetable generation
- **Reviewer**: View and approve timetables

### 2. Infrastructure Management
- Academic Blocks
- Floors within blocks
- Rooms with capacity, type, and allocatable status

### 3. Academic Management
- Departments
- Batches with fixed room support
- Faculty with workload limits
- Subjects with frequency and duration
- Faculty-Subject-Batch mappings

### 4. Intelligent Scheduling
**Hard Constraints:**
- No room clashes
- No faculty clashes
- No batch clashes
- Weekly subject frequency requirements
- Max classes per day per batch
- Room capacity ≥ batch strength
- Batch fixed-room constraints
- Locked manual entries preserved
- Working hours: 10 AM - 6 PM

**Soft Constraints:**
- Balanced faculty workload
- Minimized schedule gaps
- Maximized room utilization

### 5. Special Features
- **Batch Fixed Room**: Assign a specific room to a batch (e.g., EB → Room 7025)
- **Locked Entries**: Mark manual entries as fixed to preserve during regeneration
- **Responsive UI**: Modern dashboard with sidebar navigation
- **Print-Friendly**: Timetable view optimized for printing

## 🚀 Installation & Setup

See [SETUP.md](SETUP.md) for detailed instructions.

Quick start:
```bash
cd university_scheduler
pip install -r requirements.txt
python manage.py migrate
python manage.py init_sample_data
python manage.py runserver
```

## 📊 Database Models

### User Model
- Custom user with role field (admin/coordinator/reviewer)

### Infrastructure Models
- **AcademicBlock**: Building blocks
- **Floor**: Floors within blocks
- **Room**: Classrooms/labs with capacity and type

### Academic Models
- **Department**: Academic departments
- **Batch**: Student groups with semester, section, strength
- **Faculty**: Teaching staff with workload limits
- **Subject**: Courses with type and frequency
- **FacultySubject**: Mapping between faculty, subject, and batch

### Timetable Models
- **TimetableEntry**: Individual schedule entries
- **TimetableGeneration**: Generation history and status

## 🎨 UI/UX Design

### Layout
- Left sidebar navigation
- Top header with user info
- Main content area with cards
- Responsive design for mobile

### Color Scheme
- Primary: #4A90E2 (Blue)
- Secondary: #7B8794 (Gray)
- Success: #5CB85C (Green)
- Danger: #D9534F (Red)
- Background: #F5F7FA (Light Gray)

### Components
- Stat cards with hover effects
- Data tables with sorting
- Form inputs with validation
- Loading spinner for generation
- Alert messages with auto-hide
- Timetable grid with color coding

## 🔧 OR-Tools Solver Implementation

Located in `scheduler_engine/solver.py`:

1. **Variable Creation**: Boolean variables for each possible (batch, subject, faculty, day, time, room) combination
2. **Constraint Addition**: Hard constraints enforced through CP-SAT
3. **Objective Function**: Soft constraints optimized
4. **Solution Extraction**: Convert solver output to timetable entries

## 📝 Usage Workflow

1. **Admin Setup**:
   - Create blocks, floors, rooms
   - Set room capacities and types

2. **Academic Configuration**:
   - Add departments
   - Create batches (set fixed room if needed)
   - Add faculty members
   - Create subjects
   - Map faculty to subjects and batches

3. **Manual Entries** (Optional):
   - Create fixed timetable entries
   - Mark as locked to preserve

4. **Generate Timetable**:
   - Navigate to "Generate Timetable"
   - Click generate button
   - Wait for solver to complete
   - View results

5. **Review**:
   - Select batch to view timetable
   - Print or export if needed

## 🔐 Security Considerations

- CSRF protection enabled
- Password validation
- Role-based access control
- Login required decorators
- SQL injection prevention (Django ORM)

## 📈 Scalability

- Modular architecture
- Separate scheduling engine
- Database-agnostic (SQLite → PostgreSQL)
- Efficient constraint solving
- Optimized queries with select_related

## 🐛 Troubleshooting

**Timetable generation fails:**
- Check faculty-subject mappings exist
- Verify room capacities are sufficient
- Reduce fixed constraints if too restrictive

**Solver timeout:**
- Increase time limit in solver.py
- Reduce number of batches/subjects
- Simplify constraints

**Static files not loading:**
- Ensure DEBUG=True in development
- Check STATIC_URL and STATICFILES_DIRS

## 🚢 Production Deployment

1. Update settings:
   - DEBUG=False
   - ALLOWED_HOSTS=['yourdomain.com']
   - SECRET_KEY from environment
   - PostgreSQL database

2. Static files:
   ```bash
   python manage.py collectstatic
   ```

3. WSGI server:
   ```bash
   gunicorn scheduler_project.wsgi:application
   ```

4. Nginx configuration for reverse proxy

5. SSL/TLS certificate setup

## 📚 Technology Stack

- **Backend**: Django 4.2
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Optimization**: Google OR-Tools 9.8
- **Frontend**: HTML5, CSS3, JavaScript (ES6)
- **Template Engine**: Django Templates
- **Authentication**: Django Auth System

## 🎓 NEP 2020 Alignment

- Flexible credit system support
- Elective course handling
- Multi-disciplinary approach
- Semester-based structure
- Choice-based credit system ready

## 📄 License

Educational and institutional use.

## 👥 Support

For issues:
1. Check troubleshooting section
2. Review Django documentation
3. Consult OR-Tools documentation

## 🔄 Future Enhancements

- PDF export functionality
- Email notifications
- Conflict resolution suggestions
- Multi-semester planning
- Faculty preference handling
- Room preference by subject type
- Break time optimization
- Academic calendar integration
