from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
import csv
import io
from .models import (
    AcademicBlock, Floor, Room, Department, Batch, Faculty, 
    Subject, FacultySubject, TimetableEntry, TimetableGeneration, BatchSubject, FacultySubjectCapability
)
from .forms import (
    AcademicBlockForm, FloorForm, RoomForm, DepartmentForm, 
    BatchForm, FacultyForm, SubjectForm, FacultySubjectForm, TimetableEntryForm,
    FacultyCSVUploadForm, SubjectCSVUploadForm, BatchSubjectCSVUploadForm
)
from scheduler_engine.solver import TimetableSolver


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


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
    batches = Batch.objects.select_related('department', 'fixed_room').prefetch_related('batch_subjects__subject').all()
    return render(request, 'academic/batch_list.html', {'batches': batches})


@login_required
def batch_detail(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    batch_subjects = BatchSubject.objects.filter(batch=batch).select_related('subject')
    return render(request, 'academic/batch_detail.html', {'batch': batch, 'batch_subjects': batch_subjects})


@login_required
def batch_subjects_view(request):
    department_id = request.GET.get('department')
    year = request.GET.get('year')
    semester = request.GET.get('semester')
    
    batch_subjects = BatchSubject.objects.select_related('batch__department', 'subject').all()
    
    if department_id:
        batch_subjects = batch_subjects.filter(batch__department_id=department_id)
    if year:
        batch_subjects = batch_subjects.filter(batch__year=year)
    if semester:
        batch_subjects = batch_subjects.filter(batch__semester=semester)
    
    batch_subjects = batch_subjects.order_by('batch__department', 'batch__year', 'batch__semester', 'batch__section', 'subject__code')
    
    # Group by batch
    from collections import defaultdict
    batches_data = defaultdict(list)
    for bs in batch_subjects:
        batches_data[bs.batch].append(bs.subject)
    
    departments = Department.objects.all()
    
    context = {
        'batches_data': dict(batches_data),
        'departments': departments,
        'selected_department': department_id,
        'selected_year': year,
        'selected_semester': semester,
    }
    return render(request, 'academic/batch_subjects_view.html', context)


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


@login_required
@role_required(['admin', 'coordinator'])
def batch_subject_upload_csv(request):
    if request.method == 'POST':
        form = BatchSubjectCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            department = form.cleaned_data['department']
            year = form.cleaned_data['year']
            semester = form.cleaned_data['semester']
            
            try:
                decoded_file = csv_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)
                
                created_batches = 0
                updated_batches = 0
                linked_subjects = 0
                errors = []
                
                for idx, row in enumerate(reader, start=2):
                    section = row.get('section', '').strip()
                    
                    if not section:
                        errors.append(f"Row {idx}: section is required")
                        continue
                    
                    batch, created = Batch.objects.get_or_create(
                        department=department,
                        year=year,
                        semester=semester,
                        section=section,
                        defaults={'strength': 60, 'max_classes_per_day': 6}
                    )
                    
                    if created:
                        created_batches += 1
                    else:
                        updated_batches += 1
                    
                    # Process ALL columns except 'section' as potential subject codes
                    for key, value in row.items():
                        if key.lower() != 'section' and value and value.strip():
                            subject_code = value.strip()
                            try:
                                subject = Subject.objects.get(code=subject_code)
                                _, link_created = BatchSubject.objects.get_or_create(batch=batch, subject=subject)
                                if link_created:
                                    linked_subjects += 1
                            except Subject.DoesNotExist:
                                errors.append(f"Row {idx}, Column '{key}': Subject '{subject_code}' not found")
                
                if errors:
                    error_msg = '; '.join(errors[:10])  # Show first 10 errors
                    if len(errors) > 10:
                        error_msg += f' ... and {len(errors) - 10} more errors'
                    messages.warning(request, f'Created {created_batches} batches, updated {updated_batches} batches, linked {linked_subjects} new subjects. Errors: {error_msg}')
                else:
                    messages.success(request, f'Successfully created {created_batches} batches, updated {updated_batches} batches, and linked {linked_subjects} new subjects.')
                return redirect('batch_subjects_view')
            
            except Exception as e:
                messages.error(request, f'Error processing CSV: {str(e)}')
    else:
        form = BatchSubjectCSVUploadForm()
    
    return render(request, 'forms/batch_subject_csv_upload.html', {'form': form, 'title': 'Upload Batch-Subject CSV'})


# Faculty Views
@login_required
def faculty_list(request):
    faculty_list = Faculty.objects.select_related('department').prefetch_related(
        'subject_capabilities__subject',
        'subject_assignments__subject', 
        'subject_assignments__batch'
    ).all()
    
    # Group subjects by faculty - get unique subjects from capabilities
    from collections import defaultdict
    faculty_subjects = defaultdict(list)
    for f in faculty_list:
        # First, get subjects from capabilities (subjects they CAN teach)
        for capability in f.subject_capabilities.all():
            faculty_subjects[f.id].append(capability.subject)
    
    return render(request, 'academic/faculty_list.html', {'faculty': faculty_list, 'faculty_subjects': dict(faculty_subjects)})


@login_required
def faculty_detail(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    faculty_subjects = FacultySubject.objects.filter(faculty=faculty).select_related('subject', 'batch__department')
    
    # Group by subject
    from collections import defaultdict
    subjects_data = defaultdict(list)
    for fs in faculty_subjects:
        subjects_data[fs.subject].append(fs.batch)
    
    return render(request, 'academic/faculty_detail.html', {
        'faculty': faculty,
        'subjects_data': dict(subjects_data),
        'total_assignments': faculty_subjects.count()
    })


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


@login_required
@role_required(['admin', 'coordinator'])
def faculty_upload_csv(request):
    if request.method == 'POST':
        form = FacultyCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            department = form.cleaned_data['department']
            assign_to_batches = form.cleaned_data.get('assign_to_batches', False)
            
            try:
                decoded_file = csv_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)
                
                created_faculty_count = 0
                skipped_faculty_count = 0
                linked_capabilities_count = 0
                linked_batch_assignments_count = 0
                total_subjects_found = 0
                errors = []
                
                for idx, row in enumerate(reader, start=2):
                    teacher_name = row.get('Teach-name', '').strip()
                    employee_id = row.get('Emp-ID', '').strip()
                    email = row.get('email', '').strip()
                    
                    if not teacher_name:
                        errors.append(f"Row {idx}: Teach-name is required")
                        continue
                    
                    if not employee_id:
                        errors.append(f"Row {idx}: Emp-ID is required")
                        continue
                    
                    # Extract subject codes from remaining columns
                    subject_codes = []
                    for key, value in row.items():
                        if key.lower() not in ['teach-name', 'emp-id', 'email'] and value and value.strip():
                            subject_codes.append(value.strip())
                    
                    # Validate that at least one subject is provided
                    if not subject_codes:
                        errors.append(f"Row {idx}: At least one subject code is required for {teacher_name}")
                        continue
                    
                    total_subjects_found += len(subject_codes)
                    
                    # Create or get faculty
                    faculty, faculty_created = Faculty.objects.get_or_create(
                        employee_id=employee_id,
                        defaults={
                            'name': teacher_name,
                            'department': department,
                            'email': email,
                            'max_hours_per_week': 20
                        }
                    )
                    
                    if faculty_created:
                        created_faculty_count += 1
                    else:
                        skipped_faculty_count += 1
                    
                    # ALWAYS create FacultySubjectCapability (subjects faculty CAN teach)
                    for subject_code in subject_codes:
                        try:
                            subject = Subject.objects.get(code=subject_code)
                            _, capability_created = FacultySubjectCapability.objects.get_or_create(
                                faculty=faculty,
                                subject=subject
                            )
                            if capability_created:
                                linked_capabilities_count += 1
                        except Subject.DoesNotExist:
                            errors.append(f"Row {idx}: Subject '{subject_code}' not found. Create subject first.")
                    
                    # OPTIONALLY create FacultySubject (batch assignments)
                    if assign_to_batches:
                        batches = Batch.objects.filter(department=department)
                        if not batches.exists():
                            errors.append(f"Row {idx}: No batches found in department {department.code}. Skipping batch assignments.")
                        else:
                            for subject_code in subject_codes:
                                try:
                                    subject = Subject.objects.get(code=subject_code)
                                    for batch in batches:
                                        _, link_created = FacultySubject.objects.get_or_create(
                                            faculty=faculty,
                                            subject=subject,
                                            batch=batch
                                        )
                                        if link_created:
                                            linked_batch_assignments_count += 1
                                except Subject.DoesNotExist:
                                    pass  # Already reported above
                
                if errors:
                    error_msg = '; '.join(errors[:10])
                    if len(errors) > 10:
                        error_msg += f' ... and {len(errors) - 10} more errors'
                    messages.warning(request, f'Created {created_faculty_count} faculty, skipped {skipped_faculty_count} duplicates, linked {linked_capabilities_count} subject capabilities. Errors: {error_msg}')
                else:
                    if assign_to_batches:
                        messages.success(request, f'Successfully created {created_faculty_count} faculty members, skipped {skipped_faculty_count} duplicates. Linked {linked_capabilities_count} subject capabilities and {linked_batch_assignments_count} batch assignments. All {total_subjects_found} subjects are now visible in faculty list!')
                    else:
                        messages.success(request, f'Successfully created {created_faculty_count} faculty members, skipped {skipped_faculty_count} duplicates. Linked {linked_capabilities_count} subject capabilities. All {total_subjects_found} subjects are now visible in faculty list!')
                return redirect('faculty_list')
            
            except Exception as e:
                messages.error(request, f'Error processing CSV: {str(e)}')
    else:
        form = FacultyCSVUploadForm()
    
    return render(request, 'forms/faculty_csv_upload.html', {'form': form, 'title': 'Upload Faculty CSV'})


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


@login_required
@role_required(['admin', 'coordinator'])
def subject_upload_csv(request):
    if request.method == 'POST':
        form = SubjectCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            department = form.cleaned_data['department']
            subject_type = form.cleaned_data['subject_type']
            duration_hours = form.cleaned_data['duration_hours']
            
            try:
                decoded_file = csv_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.DictReader(io_string)
                
                created_count = 0
                skipped_count = 0
                errors = []
                
                for idx, row in enumerate(reader, start=2):
                    subject_code = row.get('subject-code', '').strip()
                    subject_name = row.get('subject-name', '').strip()
                    weekly_frequency = row.get('weekly-frequency', '').strip()
                    
                    if not subject_code:
                        errors.append(f"Row {idx}: subject-code is required")
                        continue
                    
                    if not subject_name:
                        errors.append(f"Row {idx}: subject-name is required")
                        continue
                    
                    if not weekly_frequency:
                        errors.append(f"Row {idx}: weekly-frequency is required")
                        continue
                    
                    try:
                        weekly_frequency = int(weekly_frequency)
                    except ValueError:
                        errors.append(f"Row {idx}: weekly-frequency must be a number")
                        continue
                    
                    if not Subject.objects.filter(code=subject_code).exists():
                        Subject.objects.create(
                            name=subject_name,
                            code=subject_code,
                            subject_type=subject_type,
                            weekly_frequency=weekly_frequency,
                            duration_hours=duration_hours,
                            department=department
                        )
                        created_count += 1
                    else:
                        skipped_count += 1
                
                if errors:
                    messages.warning(request, f'Created {created_count} subjects. Errors: {"; ".join(errors[:5])}')
                else:
                    messages.success(request, f'Successfully created {created_count} subjects. Skipped {skipped_count} duplicates.')
                return redirect('subject_list')
            
            except Exception as e:
                messages.error(request, f'Error processing CSV: {str(e)}')
    else:
        form = SubjectCSVUploadForm()
    
    return render(request, 'forms/subject_csv_upload.html', {'form': form, 'title': 'Upload Subject CSV'})


# Faculty-Subject Mapping
@login_required
def faculty_subject_list(request):
    # Get both types of mappings
    batch_mappings = FacultySubject.objects.select_related('faculty', 'subject', 'batch').all()
    capability_mappings = FacultySubjectCapability.objects.select_related('faculty', 'subject').all()
    
    return render(request, 'academic/faculty_subject_list.html', {
        'batch_mappings': batch_mappings,
        'capability_mappings': capability_mappings
    })


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
