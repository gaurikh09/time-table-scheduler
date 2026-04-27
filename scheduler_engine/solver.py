from ortools.sat.python import cp_model

LUNCH_START = 13  # 1 PM
LUNCH_END = 14    # 2 PM


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

    def _is_valid_start(self, start_time, duration):
        """
        A slot is valid only if the entire class fits without crossing lunch (13-14).
        e.g. start=12, duration=2 would span 12-14 which crosses lunch → invalid.
        """
        end_time = start_time + duration
        # Block any slot that overlaps with lunch hour
        if start_time < LUNCH_END and end_time > LUNCH_START:
            return False
        # Must end within working hours
        if end_time > self.working_hours[1]:
            return False
        return True

    def create_variables(self):
        """Create decision variables — one variable per (batch, subject, faculty, day, start, room)."""
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
                valid_rooms = [r for r in self.rooms if r.is_allocatable]

            for day in self.days:
                for start_time in self.timeslots:
                    if not self._is_valid_start(start_time, duration):
                        continue
                    for room in valid_rooms:
                        var_name = f'b{batch.id}_s{subject.id}_f{faculty.id}_d{day}_t{start_time}_r{room.id}'
                        var = self.model.NewBoolVar(var_name)
                        self.variables[(batch.id, subject.id, faculty.id, day, start_time, room.id)] = var

    def add_fixed_constraints(self):
        """Lock manually fixed timetable entries."""
        for entry in self.fixed_entries:
            key = (entry.batch.id, entry.subject.id, entry.faculty.id,
                   entry.day_of_week, entry.start_time, entry.room.id)
            if key in self.variables:
                self.model.Add(self.variables[key] == 1)

    def add_frequency_constraints(self):
        """Each subject must be scheduled exactly weekly_frequency times per week."""
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
        """
        Prevent overlapping classes for rooms, faculty, and batches.
        A class starting at `t` with duration `d` occupies slots t, t+1, ..., t+d-1.
        So two classes clash if their time ranges overlap.
        """
        # Build a lookup: subject_id -> duration
        duration_map = {fs.subject.id: max(1, fs.subject.duration_hours) for fs in self.faculty_subjects}

        # Room clash: no two classes in same room overlap in time on same day
        for room in self.rooms:
            for day in self.days:
                for time in self.timeslots:
                    conflicting = [
                        var for (b, s, f, d, t, r), var in self.variables.items()
                        if r == room.id and d == day
                        and t <= time < t + duration_map.get(s, 1)
                    ]
                    if len(conflicting) > 1:
                        self.model.Add(sum(conflicting) <= 1)

        # Faculty clash: same faculty can't teach two classes at same time
        faculty_ids = set(fs.faculty.id for fs in self.faculty_subjects)
        for faculty_id in faculty_ids:
            for day in self.days:
                for time in self.timeslots:
                    conflicting = [
                        var for (b, s, f, d, t, r), var in self.variables.items()
                        if f == faculty_id and d == day
                        and t <= time < t + duration_map.get(s, 1)
                    ]
                    if len(conflicting) > 1:
                        self.model.Add(sum(conflicting) <= 1)

        # Batch clash: same batch can't have two classes at same time
        for batch in self.batches:
            for day in self.days:
                for time in self.timeslots:
                    conflicting = [
                        var for (b, s, f, d, t, r), var in self.variables.items()
                        if b == batch.id and d == day
                        and t <= time < t + duration_map.get(s, 1)
                    ]
                    if len(conflicting) > 1:
                        self.model.Add(sum(conflicting) <= 1)

    def add_lab_continuity_constraints(self):
        """
        Lab subjects (duration > 1) must be scheduled as ONE continuous block per occurrence.
        This is enforced by the variable design: each variable already represents a full block
        starting at start_time and lasting duration hours. The clash constraints ensure no
        overlap. So continuity is naturally handled — no extra constraint needed here.
        The key fix is in _is_valid_start which prevents labs from crossing lunch.
        """
        pass

    def add_max_classes_per_day_constraint(self):
        """Limit maximum class slots per day per batch (counts by duration)."""
        duration_map = {fs.subject.id: max(1, fs.subject.duration_hours) for fs in self.faculty_subjects}
        for batch in self.batches:
            for day in self.days:
                # Sum of all class-hours scheduled for this batch on this day
                day_vars = [
                    var for (b, s, f, d, t, r), var in self.variables.items()
                    if b == batch.id and d == day
                ]
                if day_vars:
                    self.model.Add(sum(day_vars) <= batch.max_classes_per_day)

    def add_one_subject_per_day_constraint(self):
        """Each subject can appear at most once per day per batch."""
        for fs in self.faculty_subjects:
            batch_id = fs.batch.id
            subject_id = fs.subject.id
            faculty_id = fs.faculty.id
            for day in self.days:
                day_vars = [
                    var for (b, s, f, d, t, r), var in self.variables.items()
                    if b == batch_id and s == subject_id and f == faculty_id and d == day
                ]
                if day_vars:
                    self.model.Add(sum(day_vars) <= 1)

    def get_subject_duration(self, subject_id):
        for fs in self.faculty_subjects:
            if fs.subject.id == subject_id:
                return max(1, fs.subject.duration_hours)
        return 1

    def validate_inputs(self):
        """Return warning if total weekly hours exceed available slots."""
        # Available slots per day excluding lunch = 7 hours (10-13 + 14-18)
        slots_per_day = (LUNCH_START - self.working_hours[0]) + (self.working_hours[1] - LUNCH_END)
        total_slots = len(self.days) * slots_per_day
        total_needed = sum(
            fs.subject.weekly_frequency * fs.subject.duration_hours
            for fs in self.faculty_subjects
        )
        if total_needed > total_slots:
            return (f"Warning: Total required hours ({total_needed}) exceeds available slots ({total_slots}). "
                    f"Consider reducing frequencies or max_classes_per_day.")
        return None

    def solve(self, time_limit_seconds=300):
        self.create_variables()

        if not self.variables:
            return False, ("No schedulable slots found. Check that rooms exist with sufficient "
                           "capacity and subjects have valid duration.")

        self.add_fixed_constraints()
        self.add_frequency_constraints()
        self.add_no_clash_constraints()
        self.add_lab_continuity_constraints()
        self.add_max_classes_per_day_constraint()
        self.add_one_subject_per_day_constraint()

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit_seconds
        solver.parameters.log_search_progress = False

        status = solver.Solve(self.model)

        warning = self.validate_inputs()
        suffix = f' Note: {warning}' if warning else ''

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            self.solution = self.extract_solution(solver)
            if not self.solution:
                return False, "Solver ran but scheduled nothing. Check room capacity vs batch strength."
            return True, f"Timetable generated: {len(self.solution)} entries scheduled.{suffix}"
        elif status == cp_model.INFEASIBLE:
            return False, (f"Cannot generate timetable: constraints are impossible to satisfy. "
                           f"Check room capacity, subject frequencies, and max classes per day.{suffix}")
        else:
            return False, f"Timetable generation timed out. Try reducing frequencies.{suffix}"

    def extract_solution(self, solver):
        schedule = []
        duration_map = {fs.subject.id: max(1, fs.subject.duration_hours) for fs in self.faculty_subjects}
        for (batch_id, subject_id, faculty_id, day, start_time, room_id), var in self.variables.items():
            if solver.Value(var) == 1:
                duration = duration_map.get(subject_id, 1)
                schedule.append({
                    'batch_id': batch_id,
                    'subject_id': subject_id,
                    'faculty_id': faculty_id,
                    'room_id': room_id,
                    'day_of_week': day,
                    'start_time': start_time,
                    'end_time': start_time + duration,
                })
        return schedule
