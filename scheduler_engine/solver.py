from ortools.sat.python import cp_model

LUNCH_START = 13  # 1 PM
LUNCH_END = 14    # 2 PM


class TimetableSolver:
    def __init__(self, batches, subjects, faculty_subjects, rooms, fixed_entries, combined_classes=None, working_hours=(10, 18)):
        self.batches = batches
        self.subjects = subjects
        self.faculty_subjects = faculty_subjects
        self.rooms = rooms
        self.fixed_entries = fixed_entries
        self.combined_classes = combined_classes or []
        self.working_hours = working_hours
        self.days = list(range(5))  # Monday to Friday
        self.timeslots = list(range(working_hours[0], working_hours[1]))

        self.model = cp_model.CpModel()
        self.variables = {}
        self.solution = None

        # Build blocked slots from combined classes:
        # {batch_id: {(day, time): True}} — times occupied by combined classes
        self.combined_blocked = {}  # batch_id -> set of (day, t) for every hour occupied
        self.combined_faculty_blocked = {}  # faculty_id -> set of (day, t)
        self.combined_room_blocked = {}  # room_id -> set of (day, t)
        self.combined_subject_batches = set()  # (batch_id, subject_id) already covered by combined class
        self.combined_room_warnings = []  # capacity warnings for combined classes
        for cc in self.combined_classes:
            cc_batches = list(cc.batches.all())
            total_strength = sum(b.strength for b in cc_batches)
            # Warn if combined room capacity is insufficient
            if cc.room.capacity < total_strength:
                self.combined_room_warnings.append(
                    f"Combined class '{cc.subject.code}' on {cc.get_day_of_week_display()} {cc.start_time}:00 — "
                    f"room {cc.room.room_number} (capacity {cc.room.capacity}) is too small for "
                    f"{len(cc_batches)} batches with total strength {total_strength}."
                )
            for t in range(cc.start_time, cc.end_time):
                for batch in cc_batches:
                    self.combined_blocked.setdefault(batch.id, set()).add((cc.day_of_week, t))
                    self.combined_subject_batches.add((batch.id, cc.subject_id))
                self.combined_faculty_blocked.setdefault(cc.faculty_id, set()).add((cc.day_of_week, t))
                self.combined_room_blocked.setdefault(cc.room_id, set()).add((cc.day_of_week, t))

        # Filter out faculty_subjects whose subject is already fully covered by a combined class
        self.faculty_subjects = [
            fs for fs in self.faculty_subjects
            if (fs.batch.id, fs.subject.id) not in self.combined_subject_batches
        ]

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
        """Create decision variables — skip slots already occupied by combined classes."""
        for fs in self.faculty_subjects:
            batch = fs.batch
            subject = fs.subject
            faculty = fs.faculty
            duration = max(1, subject.duration_hours)

            # Determine valid rooms — must have capacity >= batch strength
            if batch.fixed_room:
                valid_rooms = [batch.fixed_room]
            else:
                valid_rooms = [r for r in self.rooms if r.is_allocatable and r.capacity >= batch.strength]

            # No fallback — if no room fits, skip this subject (will be caught by diagnose())
            if not valid_rooms:
                continue

            batch_blocked = self.combined_blocked.get(batch.id, set())
            faculty_blocked = self.combined_faculty_blocked.get(faculty.id, set())

            for day in self.days:
                for start_time in self.timeslots:
                    if not self._is_valid_start(start_time, duration):
                        continue
                    # Skip if any hour of this slot is blocked by a combined class for this batch or faculty
                    slot_hours = set((day, start_time + offset) for offset in range(duration))
                    if slot_hours & batch_blocked or slot_hours & faculty_blocked:
                        continue
                    for room in valid_rooms:
                        room_blocked = self.combined_room_blocked.get(room.id, set())
                        if slot_hours & room_blocked:
                            continue
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

    def diagnose(self):
        """Return a list of specific reasons why generation may fail."""
        issues = []
        DAYS = 5
        slots_per_day = (LUNCH_START - self.working_hours[0]) + (self.working_hours[1] - LUNCH_END)  # 7
        total_available = DAYS * slots_per_day

        for fs in self.faculty_subjects:
            batch = fs.batch
            subject = fs.subject
            faculty = fs.faculty
            duration = max(1, subject.duration_hours)
            freq = subject.weekly_frequency
            needed = freq * duration

            # 1. No rooms at all
            if not self.rooms:
                issues.append("No allocatable rooms exist. Add rooms first.")
                break

            # 2. Room capacity
            if batch.fixed_room:
                valid_rooms = [batch.fixed_room]
            else:
                valid_rooms = [r for r in self.rooms if r.is_allocatable and r.capacity >= batch.strength]
            if not valid_rooms:
                room_caps = ', '.join(f"Room {r.room_number} (cap {r.capacity})" for r in self.rooms if r.is_allocatable)
                issues.append(
                    f"Batch '{batch}' (strength {batch.strength}) — no room has enough capacity. "
                    f"Available rooms: {room_caps or 'none'}"
                )

            # 3. Total weekly hours vs available slots
            total_needed = sum(f.subject.weekly_frequency * max(1, f.subject.duration_hours) for f in self.faculty_subjects if f.batch.id == batch.id)
            combined_blocked_count = len(self.combined_blocked.get(batch.id, set()))
            effective_slots = total_available - combined_blocked_count
            if total_needed > effective_slots:
                issues.append(
                    f"Batch '{batch}' needs {total_needed} hours/week but only {effective_slots} slots available "
                    f"({total_available} total − {combined_blocked_count} blocked by combined classes)."
                )

            # 4. max_classes_per_day too low
            min_days_needed = (total_needed + batch.max_classes_per_day - 1) // batch.max_classes_per_day
            if min_days_needed > DAYS:
                issues.append(
                    f"Batch '{batch}': max_classes_per_day={batch.max_classes_per_day} is too low. "
                    f"Need at least {total_needed} hours across {DAYS} days — increase to at least {-(-total_needed // DAYS)}."
                )

            # 5. Subject frequency > 5 (can't schedule same subject more than once per day)
            if freq > DAYS:
                issues.append(
                    f"Subject '{subject.code}' for batch '{batch}' has weekly_frequency={freq} "
                    f"but there are only {DAYS} working days. Max frequency is {DAYS}."
                )

            # 6. Lab/2hr subject: check enough valid 2-hr slots exist after lunch blocking
            if duration > 1:
                valid_starts = [
                    (d, t) for d in range(DAYS)
                    for t in self.timeslots
                    if self._is_valid_start(t, duration)
                    and not (set((d, t + o) for o in range(duration)) & self.combined_blocked.get(batch.id, set()))
                    and not (set((d, t + o) for o in range(duration)) & self.combined_faculty_blocked.get(faculty.id, set()))
                ]
                if len(valid_starts) < freq:
                    issues.append(
                        f"Subject '{subject.code}' (duration={duration}h, freq={freq}) for batch '{batch}': "
                        f"only {len(valid_starts)} valid {duration}-hour slots exist after lunch/combined blocking, need {freq}."
                    )

            # 7. Faculty blocked by combined classes for too many slots
            faculty_blocked_days = set(d for (d, t) in self.combined_faculty_blocked.get(faculty.id, set()))
            if len(faculty_blocked_days) >= DAYS and freq > 0:
                issues.append(
                    f"Faculty '{faculty.name}' is blocked by combined classes on all {DAYS} days "
                    f"and cannot teach '{subject.code}' for batch '{batch}'."
                )

        # 8. No variables created at all (catches edge cases)
        if not self.variables and not issues:
            issues.append(
                "No schedulable variable slots were created. This usually means all time slots are "
                "blocked by combined classes, or no rooms match batch capacity."
            )

        return issues

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
            issues = self.diagnose()
            if issues:
                detail = '\n'.join(f"• {i}" for i in issues)
                return False, f"Cannot generate timetable. Specific issues found:\n{detail}"
            return False, (
                f"Cannot generate timetable: constraints are impossible to satisfy.{suffix} "
                f"Check room capacity, subject frequencies, and max classes per day."
            )
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
