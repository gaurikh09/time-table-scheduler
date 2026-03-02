from django.core.management.base import BaseCommand
from core.models import (
    User, AcademicBlock, Floor, Room, Department, Batch, 
    Faculty, Subject, FacultySubject
)

class Command(BaseCommand):
    help = 'Initialize database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create users
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@university.edu', 'admin123', role='admin')
            self.stdout.write(self.style.SUCCESS('Admin user created (username: admin, password: admin123)'))
        
        if not User.objects.filter(username='coordinator').exists():
            User.objects.create_user('coordinator', 'coord@university.edu', 'coord123', role='coordinator')
            self.stdout.write(self.style.SUCCESS('Coordinator user created'))
        
        # Create infrastructure
        block, _ = AcademicBlock.objects.get_or_create(code='AB', defaults={'name': 'Academic Block A'})
        floor7, _ = Floor.objects.get_or_create(block=block, floor_number=7)
        
        Room.objects.get_or_create(
            floor=floor7, room_number='7025',
            defaults={'capacity': 60, 'room_type': 'classroom', 'is_allocatable': True}
        )
        Room.objects.get_or_create(
            floor=floor7, room_number='7026',
            defaults={'capacity': 50, 'room_type': 'classroom', 'is_allocatable': True}
        )
        Room.objects.get_or_create(
            floor=floor7, room_number='7027',
            defaults={'capacity': 40, 'room_type': 'lab', 'is_allocatable': True}
        )
        self.stdout.write(self.style.SUCCESS('Infrastructure created'))
        
        # Create departments
        cse, _ = Department.objects.get_or_create(code='CSE', defaults={'name': 'Computer Science & Engineering'})
        ece, _ = Department.objects.get_or_create(code='ECE', defaults={'name': 'Electronics & Communication'})
        self.stdout.write(self.style.SUCCESS('Departments created'))
        
        # Create batches
        room_7025 = Room.objects.get(room_number='7025')
        batch_eb, _ = Batch.objects.get_or_create(
            department=cse, year=2, semester=3, section='EB',
            defaults={'strength': 55, 'max_classes_per_day': 6, 'fixed_room': room_7025}
        )
        batch_ea, _ = Batch.objects.get_or_create(
            department=cse, year=2, semester=3, section='EA',
            defaults={'strength': 50, 'max_classes_per_day': 6}
        )
        self.stdout.write(self.style.SUCCESS('Batches created'))
        
        # Create faculty
        faculty1, _ = Faculty.objects.get_or_create(
            employee_id='F001',
            defaults={'name': 'Dr. Rajesh Kumar', 'department': cse, 'email': 'rajesh@university.edu', 'max_hours_per_week': 20}
        )
        faculty2, _ = Faculty.objects.get_or_create(
            employee_id='F002',
            defaults={'name': 'Dr. Priya Sharma', 'department': cse, 'email': 'priya@university.edu', 'max_hours_per_week': 18}
        )
        self.stdout.write(self.style.SUCCESS('Faculty created'))
        
        # Create subjects
        ds, _ = Subject.objects.get_or_create(
            code='CS301',
            defaults={'name': 'Data Structures', 'subject_type': 'theory', 'weekly_frequency': 4, 'duration_hours': 1, 'department': cse}
        )
        algo, _ = Subject.objects.get_or_create(
            code='CS302',
            defaults={'name': 'Algorithms', 'subject_type': 'theory', 'weekly_frequency': 3, 'duration_hours': 1, 'department': cse}
        )
        dbms, _ = Subject.objects.get_or_create(
            code='CS303',
            defaults={'name': 'Database Management', 'subject_type': 'theory', 'weekly_frequency': 3, 'duration_hours': 1, 'department': cse}
        )
        self.stdout.write(self.style.SUCCESS('Subjects created'))
        
        # Create faculty-subject mappings
        FacultySubject.objects.get_or_create(faculty=faculty1, subject=ds, batch=batch_eb)
        FacultySubject.objects.get_or_create(faculty=faculty2, subject=algo, batch=batch_eb)
        FacultySubject.objects.get_or_create(faculty=faculty1, subject=dbms, batch=batch_ea)
        self.stdout.write(self.style.SUCCESS('Faculty-Subject mappings created'))
        
        self.stdout.write(self.style.SUCCESS('\nSample data initialization complete!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('  Admin: username=admin, password=admin123')
        self.stdout.write('  Coordinator: username=coordinator, password=coord123')
