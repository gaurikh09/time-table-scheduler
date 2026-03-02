from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from .models import (
    AcademicBlock, Floor, Room, Department, Batch, Faculty, 
    Subject, FacultySubject, TimetableEntry, TimetableGeneration
)
from .forms import (
    AcademicBlockForm, FloorForm, RoomForm, DepartmentForm, 
    BatchForm, FacultyForm, SubjectForm, FacultySubjectForm, TimetableEntryForm
)
from scheduler_engine.solver import TimetableSolver


def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                messages.error(request, "You don't have permission to access this page.")
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


@login_required
def dashboard(request):
    context = {
        'total_batches': Batch.objects.count(),
        'total_faculty': Faculty.objects.count(),
        'total_subjects': Subject.objects.count(),
        'total_rooms': Room.objects.filter(is_allocatable=True).count(),
        'recent_generations': TimetableGeneration.objects.all()[:5],
    }
    return render(request, 'dashboard.html', context)


# Infrastructure Views
@login_required
@role_required(['admin'])
def block_list(request):
    blocks = AcademicBlock.objects.all()
    return render(request, 'infrastructure/block_list.html', {'blocks': blocks})


@login_required
@role_required(['admin'])
def block_create(request):
    if request.method == 'POST':
        form = AcademicBlockForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Academic block created successfully.')
            return redirect('block_list')
    else:
        form = AcademicBlockForm()
    return render(request, 'forms/block_form.html', {'form': form, 'title': 'Create Block'})


@login_required
@role_required(['admin'])
def block_edit(request, pk):
    block = get_object_or_404(AcademicBlock, pk=pk)
    if request.method == 'POST':
        form = AcademicBlockForm(request.POST, instance=block)
        if form.is_valid():
            form.save()
            messages.success(request, 'Academic block updated successfully.')
            return redirect('block_list')
    else:
        form = AcademicBlockForm(instance=block)
    return render(request, 'forms/block_form.html', {'form': form, 'title': 'Edit Block'})


@login_required
@role_required(['admin'])
def block_delete(request, pk):
    block = get_object_or_404(AcademicBlock, pk=pk)
    if request.method == 'POST':
        block.delete()
        messages.success(request, 'Academic block deleted successfully.')
        return redirect('block_list')
    return render(request, 'confirm_delete.html', {'object': block, 'type': 'Block'})


@login_required
@role_required(['admin'])
def room_list(request):
    rooms = Room.objects.select_related('floor__block').all()
    return render(request, 'infrastructure/room_list.html', {'rooms': rooms})


@login_required
@role_required(['admin'])
def room_create(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room created successfully.')
            return redirect('room_list')
    else:
        form = RoomForm()
    return render(request, 'forms/room_form.html', {'form': form, 'title': 'Create Room'})


@login_required
@role_required(['admin'])
def room_edit(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room updated successfully.')
            return redirect('room_list')
    else:
        form = RoomForm(instance=room)
    return render(request, 'forms/room_form.html', {'form': form, 'title': 'Edit Room'})


# Department Views
@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'academic/department_list.html', {'departments': departments})


@login_required
@role_required(['admin', 'coordinator'])
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department created successfully.')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(request, 'forms/department_form.html', {'form': form, 'title': 'Create Department'})


# Batch Views
@login_required
def batch_list(request):
    batches = Batch.objects.select_related('department', 'fixed_room').all()
    return render(request, 'academic/batch_list.html', {'batches': batches})


@login_required
@role_required(['admin', 'coordinator'])
def batch_create(request):
    if request.method == 'POST':
        form = BatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Batch created successfully.')
            return redirect('batch_list')
    else:
        form = BatchForm()
    return render(request, 'forms/batch_form.html', {'form': form, 'title': 'Create Batch'})


@login_required
@role_required(['admin', 'coordinator'])
def batch_edit(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    if request.method == 'POST':
        form = BatchForm(request.POST, instance=batch)
        if form.is_valid():
            form.save()
            messages.success(request, 'Batch updated successfully.')
            return redirect('batch_list')
    else:
        form = BatchForm(instance=batch)
    return render(request, 'forms/batch_form.html', {'form': form, 'title': 'Edit Batch'})


# Faculty Views
@login_required
def faculty_list(request):
    faculty = Faculty.objects.select_related('department').all()
    return render(request, 'academic/faculty_list.html', {'faculty': faculty})


@login_required
@role_required(['admin', 'coordinator'])
def faculty_create(request):
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Faculty created successfully.')
            return redirect('faculty_list')
    else:
        form = FacultyForm()
    return render(request, 'forms/faculty_form.html', {'form': form, 'title': 'Create Faculty'})


# Subject Views
@login_required
def subject_list(request):
    subjects = Subject.objects.select_related('department').all()
    return render(request, 'academic/subject_list.html', {'subjects': subjects})


@login_required
@role_required(['admin', 'coordinator'])
def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject created successfully.')
            return redirect('subject_list')
    else:
        form = SubjectForm()
    return render(request, 'forms/subject_form.html', {'form': form, 'title': 'Create Subject'})


# Faculty-Subject Mapping
@login_required
def faculty_subject_list(request):
    mappings = FacultySubject.objects.select_related('faculty', 'subject', 'batch').all()
    return render(request, 'academic/faculty_subject_list.html', {'mappings': mappings})


@login_required
@role_required(['admin', 'coordinator'])
def faculty_subject_create(request):
    if request.method == 'POST':
        form = FacultySubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Faculty-Subject mapping created successfully.')
            return redirect('faculty_subject_list')
    else:
        form = FacultySubjectForm()
    return render(request, 'forms/faculty_subject_form.html', {'form': form, 'title': 'Create Mapping'})


# Timetable Generation
@login_required
@role_required(['admin', 'coordinator'])
def generate_timetable(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                generation = TimetableGeneration.objects.create(
                    generated_by=request.user,
                    status='processing'
                )
                
                # Get all data
                batches = list(Batch.objects.all())
                rooms = list(Room.objects.filter(is_allocatable=True))
                faculty_subjects = list(FacultySubject.objects.select_related('faculty', 'subject', 'batch').all())
                fixed_entries = list(TimetableEntry.objects.filter(is_fixed=True).select_related('batch', 'subject', 'faculty', 'room'))
                
                # Run solver
                solver = TimetableSolver(batches, None, faculty_subjects, rooms, fixed_entries)
                success, message = solver.solve()
                
                if success:
                    # Delete non-fixed entries
                    TimetableEntry.objects.filter(is_fixed=False).delete()
                    
                    # Create new entries
                    for entry_data in solver.solution:
                        TimetableEntry.objects.create(
                            batch_id=entry_data['batch_id'],
                            subject_id=entry_data['subject_id'],
                            faculty_id=entry_data['faculty_id'],
                            room_id=entry_data['room_id'],
                            day_of_week=entry_data['day_of_week'],
                            start_time=entry_data['start_time'],
                            end_time=entry_data['end_time'],
                            is_fixed=False
                        )
                    
                    generation.status = 'completed'
                    generation.completed_at = timezone.now()
                    generation.save()
                    
                    messages.success(request, 'Timetable generated successfully!')
                    return redirect('timetable_view')
                else:
                    generation.status = 'failed'
                    generation.error_message = message
                    generation.save()
                    messages.error(request, message)
        
        except Exception as e:
            messages.error(request, f'Error generating timetable: {str(e)}')
    
    return render(request, 'timetable/generate.html')


@login_required
def timetable_view(request):
    batch_id = request.GET.get('batch')
    batches = Batch.objects.all()
    
    if batch_id:
        entries = TimetableEntry.objects.filter(batch_id=batch_id).select_related(
            'subject', 'faculty', 'room', 'batch'
        ).order_by('day_of_week', 'start_time')
    else:
        entries = []
    
    # Organize by day and time
    timetable_grid = {}
    for entry in entries:
        day = entry.day_of_week
        if day not in timetable_grid:
            timetable_grid[day] = {}
        timetable_grid[day][entry.start_time] = entry
    
    context = {
        'batches': batches,
        'selected_batch': batch_id,
        'timetable_grid': timetable_grid,
        'days': TimetableEntry.DAYS_OF_WEEK,
        'timeslots': range(10, 18),
    }
    return render(request, 'timetable/timetable_view.html', context)


@login_required
@role_required(['admin', 'coordinator'])
def manual_entry_create(request):
    if request.method == 'POST':
        form = TimetableEntryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Manual timetable entry created successfully.')
            return redirect('timetable_view')
    else:
        form = TimetableEntryForm()
    return render(request, 'forms/timetable_entry_form.html', {'form': form, 'title': 'Create Manual Entry'})
