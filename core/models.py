from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('coordinator', 'Department Coordinator'),
        ('reviewer', 'Reviewer'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='coordinator')
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# Infrastructure Models
class AcademicBlock(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        ordering = ['code']


class Floor(models.Model):
    block = models.ForeignKey(AcademicBlock, on_delete=models.CASCADE, related_name='floors')
    floor_number = models.IntegerField()
    
    def __str__(self):
        return f"{self.block.code} - Floor {self.floor_number}"
    
    class Meta:
        ordering = ['block', 'floor_number']
        unique_together = ['block', 'floor_number']


class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ('classroom', 'Classroom'),
        ('lab', 'Laboratory'),
        ('seminar', 'Seminar Hall'),
        ('faculty_room', 'Faculty Room'),
    ]
    
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)
    is_allocatable = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Room {self.room_number} ({self.get_room_type_display()}) - Capacity: {self.capacity}"
    
    class Meta:
        ordering = ['floor', 'room_number']
        unique_together = ['floor', 'room_number']


# Academic Models
class Department(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        ordering = ['code']


class Batch(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='batches')
    year = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    section = models.CharField(max_length=10)
    strength = models.IntegerField(validators=[MinValueValidator(1)])
    max_classes_per_day = models.IntegerField(default=6, validators=[MinValueValidator(1)])
    fixed_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, 
                                    related_name='fixed_batches',
                                    help_text="If set, all classes for this batch will be in this room")
    
    def __str__(self):
        return f"{self.department.code} - Year {self.year} Sem {self.semester} - {self.section}"
    
    class Meta:
        ordering = ['department', 'year', 'semester', 'section']
        unique_together = ['department', 'year', 'semester', 'section']


class Faculty(models.Model):
    name = models.CharField(max_length=200)
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='faculty')
    email = models.EmailField()
    max_hours_per_week = models.IntegerField(default=20, validators=[MinValueValidator(1)])
    
    def __str__(self):
        return f"{self.name} ({self.employee_id})"
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Faculty'


class Subject(models.Model):
    SUBJECT_TYPE_CHOICES = [
        ('theory', 'Theory'),
        ('lab', 'Laboratory'),
        ('elective', 'Elective'),
    ]
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    subject_type = models.CharField(max_length=20, choices=SUBJECT_TYPE_CHOICES)
    weekly_frequency = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)],
                                          help_text="Number of classes per week")
    duration_hours = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        ordering = ['code']


class FacultySubject(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='subject_assignments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='faculty_assignments')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='faculty_subjects')
    
    def __str__(self):
        return f"{self.faculty.name} - {self.subject.code} - {self.batch}"
    
    class Meta:
        unique_together = ['faculty', 'subject', 'batch']


# Timetable Models
class TimetableEntry(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
    ]
    
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='timetable_entries')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.IntegerField(validators=[MinValueValidator(10), MaxValueValidator(17)],
                                     help_text="Hour in 24-hour format (10-17)")
    end_time = models.IntegerField(validators=[MinValueValidator(11), MaxValueValidator(18)],
                                   help_text="Hour in 24-hour format (11-18)")
    is_fixed = models.BooleanField(default=False, 
                                   help_text="If True, this entry is locked and won't be changed during regeneration")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.batch} - {self.subject.code} - {self.get_day_of_week_display()} {self.start_time}:00"
    
    class Meta:
        ordering = ['batch', 'day_of_week', 'start_time']
        verbose_name_plural = 'Timetable Entries'


class TimetableGeneration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"Generation {self.id} - {self.status} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-created_at']
