from ortools.sat.python import cp_model
from collections import defaultdict

class TimetableSolver:
    def __init__(self, batches, subjects, faculty_subjects, rooms, fixed_entries, working_hours=(10, 18)):
        self.batches = batches
        self.subjects = subjects
        self.faculty_subjects = faculty_subjects
        self.rooms = rooms
        self.fixed_entries = fixed_entries
        self.working_hours = working_hours
        self.days = list(range(5))  # Monday to Friday
        self.timeslots = list(range(working_hours[0], working_hours[1]))
        
        self.model = cp_model.CpModel()
        self.variables = {}
        self.solution = None
        
    def create_variables(self):
        """Create decision variables for timetable scheduling"""
        for fs in self.faculty_subjects:
            batch = fs.batch
            subject = fs.subject
            faculty = fs.faculty
            duration = max(1, subject.duration_hours)
            
            # Determine valid rooms
            if batch.fixed_room:
                valid_rooms = [batch.fixed_room]
            else:
                valid_rooms = [r for r in self.rooms if r.is_allocatable and r.capacity >= batch.strength]
            
            if not valid_rooms:
                # Fallback: use any allocatable room if none meet capacity
                valid_rooms = [r for r in self.rooms if r.is_allocatable]
            
            # Create variables for each possible slot
            # Fix: use len(timeslots) - duration to get valid start times
            max_start_index = len(self.timeslots) - duration
            for day in self.days:
                for i in range(max_start_index + 1):
                    start_time = self.timeslots[i]
                    for room in valid_rooms:
                        var_name = f'b{batch.id}_s{subject.id}_f{faculty.id}_d{day}_t{start_time}_r{room.id}'
                        var = self.model.NewBoolVar(var_name)
                        self.variables[(batch.id, subject.id, faculty.id, day, start_time, room.id)] = var
    
    def add_fixed_constraints(self):
        """Lock manually fixed timetable entries"""
        for entry in self.fixed_entries:
            key = (entry.batch.id, entry.subject.id, entry.faculty.id, 
                   entry.day_of_week, entry.start_time, entry.room.id)
            if key in self.variables:
                self.model.Add(self.variables[key] == 1)
    
    def add_frequency_constraints(self):
        """Ensure each subject is scheduled the required number of times per week"""
        total_slots = len(self.days) * len(self.timeslots)  # 5 * 8 = 40
        
        for fs in self.faculty_subjects:
            batch_id = fs.batch.id
            subject_id = fs.subject.id
            faculty_id = fs.faculty.id
            # Cap frequency to what's physically possible
            required_freq = min(fs.subject.weekly_frequency, total_slots // fs.subject.duration_hours)
            
            relevant_vars = [
                var for (b, s, f, d, t, r), var in self.variables.items()
                if b == batch_id and s == subject_id and f == faculty_id
            ]
            
            if relevant_vars:
                # Use <= instead of == so solver isn't forced to fail on tight constraints
                self.model.Add(sum(relevant_vars) <= required_freq)
                self.model.Add(sum(relevant_vars) >= min(required_freq, len(relevant_vars)))
    
    def add_no_clash_constraints(self):
        """Prevent room, faculty, and batch clashes"""
        # Room clash prevention
        for room in self.rooms:
            for day in self.days:
                for time in self.timeslots:
                    conflicting_vars = [
                        var for (b, s, f, d, t, r), var in self.variables.items()
                        if r == room.id and d == day and t <= time < t + self.get_subject_duration(s)
                    ]
                    if len(conflicting_vars) > 1:
                        self.model.Add(sum(conflicting_vars) <= 1)
        
        # Faculty clash prevention
        faculty_ids = set(fs.faculty.id for fs in self.faculty_subjects)
        for faculty_id in faculty_ids:
            for day in self.days:
                for time in self.timeslots:
                    conflicting_vars = [
                        var for (b, s, f, d, t, r), var in self.variables.items()
                        if f == faculty_id and d == day and t <= time < t + self.get_subject_duration(s)
                    ]
                    if len(conflicting_vars) > 1:
                        self.model.Add(sum(conflicting_vars) <= 1)
        
        # Batch clash prevention
        for batch in self.batches:
            for day in self.days:
                for time in self.timeslots:
                    conflicting_vars = [
                        var for (b, s, f, d, t, r), var in self.variables.items()
                        if b == batch.id and d == day and t <= time < t + self.get_subject_duration(s)
                    ]
                    if len(conflicting_vars) > 1:
                        self.model.Add(sum(conflicting_vars) <= 1)
    
    def add_max_classes_per_day_constraint(self):
        """Limit maximum classes per day for each batch"""
        for batch in self.batches:
            for day in self.days:
                day_vars = [
                    var for (b, s, f, d, t, r), var in self.variables.items()
                    if b == batch.id and d == day
                ]
                if day_vars:
                    self.model.Add(sum(day_vars) <= batch.max_classes_per_day)
    
    def add_soft_constraints(self):
        """Maximize total scheduled classes (ensures all subjects get scheduled)"""
        all_vars = list(self.variables.values())
        if all_vars:
            self.model.Maximize(sum(all_vars))
    
    def get_subject_duration(self, subject_id):
        """Get duration of a subject"""
        for fs in self.faculty_subjects:
            if fs.subject.id == subject_id:
                return fs.subject.duration_hours
        return 1
    
    def validate_inputs(self):
        """Return a warning message if inputs are likely to cause infeasibility"""
        total_slots = len(self.days) * len(self.timeslots)
        total_needed = sum(fs.subject.weekly_frequency for fs in self.faculty_subjects)
        if total_needed > total_slots:
            return (f"Warning: Total required classes ({total_needed}) exceeds available slots ({total_slots}). "
                    f"Frequencies will be capped. Consider reducing weekly_frequency values.")
        return None
    
    def solve(self, time_limit_seconds=300):
        """Solve the constraint satisfaction problem"""
        self.create_variables()
        
        if not self.variables:
            return False, "No schedulable slots found. Check that rooms exist with sufficient capacity and subjects have valid duration."
        
        self.add_fixed_constraints()
        self.add_frequency_constraints()
        self.add_no_clash_constraints()
        self.add_max_classes_per_day_constraint()
        self.add_soft_constraints()
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit_seconds
        solver.parameters.log_search_progress = False
        
        status = solver.Solve(self.model)
        
        warning = self.validate_inputs()
        suffix = f' ({warning})' if warning else ''
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            self.solution = self.extract_solution(solver)
            if not self.solution:
                return False, "Solver found a solution but no entries were scheduled. Check room capacity vs batch strength."
            return True, f"Timetable generated successfully. {len(self.solution)} entries scheduled.{suffix}"
        elif status == cp_model.INFEASIBLE:
            return False, f"Cannot generate timetable: constraints are impossible to satisfy. Check room capacity, subject frequencies, and max classes per day.{suffix}"
        else:
            return False, f"Timetable generation timed out. Try reducing subject frequencies or increasing time limit.{suffix}"
    
    def extract_solution(self, solver):
        """Extract the solution from the solver"""
        schedule = []
        for (batch_id, subject_id, faculty_id, day, start_time, room_id), var in self.variables.items():
            if solver.Value(var) == 1:
                subject = next(fs.subject for fs in self.faculty_subjects if fs.subject.id == subject_id)
                schedule.append({
                    'batch_id': batch_id,
                    'subject_id': subject_id,
                    'faculty_id': faculty_id,
                    'room_id': room_id,
                    'day_of_week': day,
                    'start_time': start_time,
                    'end_time': start_time + subject.duration_hours,
                })
        return schedule
