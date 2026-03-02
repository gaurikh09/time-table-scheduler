from django import forms
from .models import (
    AcademicBlock, Floor, Room, Department, Batch, 
    Faculty, Subject, FacultySubject, TimetableEntry
)

class AcademicBlockForm(forms.ModelForm):
    class Meta:
        model = AcademicBlock
        fields = ['name', 'code', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'code': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }


class FloorForm(forms.ModelForm):
    class Meta:
        model = Floor
        fields = ['block', 'floor_number']
        widgets = {
            'block': forms.Select(attrs={'class': 'form-input'}),
            'floor_number': forms.NumberInput(attrs={'class': 'form-input'}),
        }


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['floor', 'room_number', 'capacity', 'room_type', 'is_allocatable']
        widgets = {
            'floor': forms.Select(attrs={'class': 'form-input'}),
            'room_number': forms.TextInput(attrs={'class': 'form-input'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-input'}),
            'room_type': forms.Select(attrs={'class': 'form-input'}),
            'is_allocatable': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'code': forms.TextInput(attrs={'class': 'form-input'}),
        }


class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['department', 'year', 'semester', 'section', 'strength', 'max_classes_per_day', 'fixed_room']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-input'}),
            'year': forms.NumberInput(attrs={'class': 'form-input'}),
            'semester': forms.NumberInput(attrs={'class': 'form-input'}),
            'section': forms.TextInput(attrs={'class': 'form-input'}),
            'strength': forms.NumberInput(attrs={'class': 'form-input'}),
            'max_classes_per_day': forms.NumberInput(attrs={'class': 'form-input'}),
            'fixed_room': forms.Select(attrs={'class': 'form-input'}),
        }


class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['name', 'employee_id', 'department', 'email', 'max_hours_per_week']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-input'}),
            'department': forms.Select(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'max_hours_per_week': forms.NumberInput(attrs={'class': 'form-input'}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'subject_type', 'weekly_frequency', 'duration_hours', 'department']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'code': forms.TextInput(attrs={'class': 'form-input'}),
            'subject_type': forms.Select(attrs={'class': 'form-input'}),
            'weekly_frequency': forms.NumberInput(attrs={'class': 'form-input'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-input'}),
            'department': forms.Select(attrs={'class': 'form-input'}),
        }


class FacultySubjectForm(forms.ModelForm):
    class Meta:
        model = FacultySubject
        fields = ['faculty', 'subject', 'batch']
        widgets = {
            'faculty': forms.Select(attrs={'class': 'form-input'}),
            'subject': forms.Select(attrs={'class': 'form-input'}),
            'batch': forms.Select(attrs={'class': 'form-input'}),
        }


class TimetableEntryForm(forms.ModelForm):
    class Meta:
        model = TimetableEntry
        fields = ['batch', 'subject', 'faculty', 'room', 'day_of_week', 'start_time', 'end_time', 'is_fixed']
        widgets = {
            'batch': forms.Select(attrs={'class': 'form-input'}),
            'subject': forms.Select(attrs={'class': 'form-input'}),
            'faculty': forms.Select(attrs={'class': 'form-input'}),
            'room': forms.Select(attrs={'class': 'form-input'}),
            'day_of_week': forms.Select(attrs={'class': 'form-input'}),
            'start_time': forms.NumberInput(attrs={'class': 'form-input', 'min': 10, 'max': 17}),
            'end_time': forms.NumberInput(attrs={'class': 'form-input', 'min': 11, 'max': 18}),
            'is_fixed': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
