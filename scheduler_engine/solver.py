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
            
            # Determine valid rooms
            if batch.fixed_room:
                valid_rooms = [batch.fixed_room]
            else:
                valid_rooms = [r for r in self.rooms if r.is_allocatable and r.capacity >= batch.strength]
            
            # Create variables for each possible slot
            for day in self.days:
                for start_time in self.timeslots[:-subject.duration_hours + 1]:
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
        for fs in self.faculty_subjects:
            batch_id = fs.batch.id
            subject_id = fs.subject.id
            faculty_id = fs.faculty.id
            required_freq = fs.subject.weekly_frequency
            
            relevant_vars = [
                var for (b, s, f, d, t, r), var in self.variables.items()
                if b == batch_id and s == subject_id and f == faculty_id
            ]
            
            if relevant_vars:
                self.model.Add(sum(relevant_vars) == required_freq)
    
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
        """Add objective function to optimize faculty workload balance"""
        faculty_loads = defaultdict(list)
        
        for (b, s, f, d, t, r), var in self.variables.items():
            faculty_loads[f].append(var)
        
        # Minimize variance in faculty workload (simplified: maximize minimum load)
        if faculty_loads:
            min_load = self.model.NewIntVar(0, 100, 'min_faculty_load')
            for faculty_id, vars_list in faculty_loads.items():
                self.model.Add(sum(vars_list) >= min_load)
            self.model.Maximize(min_load)
    
    def get_subject_duration(self, subject_id):
        """Get duration of a subject"""
        for fs in self.faculty_subjects:
            if fs.subject.id == subject_id:
                return fs.subject.duration_hours
        return 1
    
    def solve(self, time_limit_seconds=300):
        """Solve the constraint satisfaction problem"""
        self.create_variables()
        self.add_fixed_constraints()
        self.add_frequency_constraints()
        self.add_no_clash_constraints()
        self.add_max_classes_per_day_constraint()
        self.add_soft_constraints()
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit_seconds
        solver.parameters.log_search_progress = False
        
        status = solver.Solve(self.model)
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            self.solution = self.extract_solution(solver)
            return True, "Timetable generated successfully"
        elif status == cp_model.INFEASIBLE:
            return False, "Cannot generate timetable: constraints are impossible to satisfy. Check room capacity, fixed allocations, and subject frequencies."
        else:
            return False, "Timetable generation timed out or failed. Try reducing constraints or increasing time limit."
    
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
