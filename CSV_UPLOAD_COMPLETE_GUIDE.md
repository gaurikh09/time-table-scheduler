# CSV Upload Features - Complete Guide

This document explains all CSV upload features available in the University Timetable Scheduler.

## Table of Contents
1. [Subject CSV Upload](#subject-csv-upload)
2. [Batch-Subject CSV Upload](#batch-subject-csv-upload)
3. [Faculty CSV Upload with Subjects](#faculty-csv-upload-with-subjects)
4. [Complete Workflow Example](#complete-workflow-example)

---

## Subject CSV Upload

### Purpose
Bulk create subjects for a department.

### Required Columns
- `subject-code`: Unique subject code (e.g., CS101)
- `subject-name`: Full subject name (e.g., Data Structures)
- `weekly-frequency`: Number of classes per week (e.g., 4)

### Form Fields
- **Department**: Select department for all subjects
- **Subject Type**: theory/lab/elective (applies to all)
- **Duration Hours**: Class duration in hours (applies to all)

### Example CSV
```csv
subject-code,subject-name,weekly-frequency
CS101,Data Structures,4
CS102,Algorithms,4
CS103,Database Systems,3
CS104,Operating Systems,4
CS105,Computer Networks,3
CS106,Software Engineering,3
```

### Sample File
- `sample_subjects.csv` (create this based on your needs)

---

## Batch-Subject CSV Upload

### Purpose
Create batches and assign subjects to them in bulk.

### Required Columns
- `section`: Batch section name (e.g., 2EA1, 2EB1)

### Subject Columns
- **ALL other columns** are treated as subject codes
- Column names don't matter - only values are used
- Empty cells are ignored

### Form Fields
- **Department**: Select department
- **Year**: Academic year (1-4)
- **Semester**: Semester number (1-8)

### Example CSV Format 1 (Simple)
```csv
section,CS101,CS102,CS103,CS104,CS105
2EA1,CS101,CS102,CS103,CS104,CS105
2EA2,CS101,CS102,CS103,CS104,CS105
2EB1,CS101,CS102,CS103,CS106,CS107
```

### Example CSV Format 2 (Descriptive Headers)
```csv
section,subject-code1,subject-code2,subject-code3,subject-code4
2EA1,CS101,CS102,CS103,CS104
2EA2,CS101,CS102,CS103,CS104
2EB1,CS101,CS102,CS103,CS106
```

### What Happens
1. Creates batches if they don't exist (default: strength=60, max_classes_per_day=6)
2. Links subjects to batches
3. Skips duplicate batch-subject links
4. Reports errors for missing subjects

### Sample Files
- `sample_batch_subjects.csv`
- `sample_batch_subjects_alternative.csv`

---

## Faculty CSV Upload with Subjects

### Purpose
Create faculty members and assign subjects they can teach.

### Required Columns
- `Teach-name`: Full faculty name (e.g., Dr. John Smith)
- `Emp-ID`: Unique employee ID (e.g., EMP001)
- **At least one subject code column** (MANDATORY)

### Optional Columns
- `email`: Faculty email address

### Subject Columns (REQUIRED)
- **At least one subject is MANDATORY**
- All columns except Teach-name, Emp-ID, email are treated as subject codes
- Column names don't matter - only values are used
- Empty cells are ignored, but each faculty must have at least one subject

### Form Fields
- **Department**: Select department for all faculty
- **Assign to batches**: Checkbox to auto-create faculty-subject-batch mappings

### Example CSV Format 1
```csv
Teach-name,Emp-ID,email,CS101,CS102,CS103
Dr. John Smith,EMP001,john.smith@university.edu,CS101,CS102,
Dr. Jane Doe,EMP002,jane.doe@university.edu,CS102,CS103,
Prof. Robert Brown,EMP003,robert.brown@university.edu,CS101,CS103,
```

### Example CSV Format 2
```csv
Teach-name,Emp-ID,email,subject1,subject2,subject3,subject4
Dr. John Smith,EMP001,john@edu,CS101,CS102,CS103,
Dr. Jane Doe,EMP002,jane@edu,CS102,CS103,CS104,
Prof. Robert Brown,EMP003,robert@edu,CS101,CS103,CS105,
```

### Assign to Batches Option

#### Unchecked (Default)
- Creates faculty members
- Validates that subjects exist
- Does NOT create faculty-subject-batch mappings
- You manually assign faculty to specific batches later

#### Checked
- Creates faculty members
- Automatically creates faculty-subject-batch mappings for ALL batches in department
- Faculty assigned to teach their subjects for every batch
- Useful when faculty teach across all batches

### What Happens
1. Creates faculty if they don't exist
2. Validates all subject codes exist
3. If "Assign to batches" is checked:
   - Creates FacultySubject mappings for all batches in department
   - Example: 1 faculty with 2 subjects × 3 batches = 6 mappings
4. Reports errors for missing subjects or batches

### Sample Files
- `sample_faculty_with_subjects.csv`
- `sample_faculty_alternative.csv`

---

## Complete Workflow Example

### Scenario
Set up Computer Science department with:
- 5 subjects
- 3 batches (2EA1, 2EA2, 2EB1)
- 3 faculty members

### Step 1: Create Subjects
**File**: `subjects.csv`
```csv
subject-code,subject-name,weekly-frequency
CS101,Data Structures,4
CS102,Algorithms,4
CS103,Database Systems,3
CS104,Operating Systems,4
CS105,Computer Networks,3
```

**Upload**:
- Navigate to Subjects → Upload CSV
- Department: Computer Science
- Subject Type: Theory
- Duration: 1 hour
- Upload file

**Result**: 5 subjects created

---

### Step 2: Create Batches with Subjects
**File**: `batches.csv`
```csv
section,CS101,CS102,CS103,CS104,CS105
2EA1,CS101,CS102,CS103,CS104,CS105
2EA2,CS101,CS102,CS103,CS104,CS105
2EB1,CS101,CS102,CS103,CS104,CS105
```

**Upload**:
- Navigate to Batches → Upload CSV
- Department: Computer Science
- Year: 2
- Semester: 3
- Upload file

**Result**: 
- 3 batches created
- 15 batch-subject links created (3 batches × 5 subjects)

---

### Step 3: Create Faculty with Subjects
**File**: `faculty.csv`
```csv
Teach-name,Emp-ID,email,CS101,CS102,CS103,CS104,CS105
Dr. John Smith,EMP001,john@edu,CS101,CS102,,,
Dr. Jane Doe,EMP002,jane@edu,,CS102,CS103,,
Prof. Robert Brown,EMP003,robert@edu,,,CS103,CS104,CS105
```

**Upload**:
- Navigate to Faculty → Upload CSV
- Department: Computer Science
- ✅ Check "Assign to batches"
- Upload file

**Result**:
- 3 faculty members created
- Dr. John Smith: 2 subjects × 3 batches = 6 mappings
- Dr. Jane Doe: 2 subjects × 3 batches = 6 mappings
- Prof. Robert Brown: 3 subjects × 3 batches = 9 mappings
- **Total: 21 faculty-subject-batch mappings created automatically**

---

### Step 4: View Results

**Batch Subjects View**:
- Navigate to Batch Subjects (sidebar)
- See all batches with their assigned subjects
- Filter by department, year, semester

**Faculty-Subject Mappings**:
- Navigate to Mappings (sidebar)
- See all faculty-subject-batch assignments
- Ready for timetable generation

---

## Important Notes

### Order Matters
1. **Always create Subjects first**
2. Then create Batches with Subjects
3. Finally create Faculty with Subjects

### Validation
- All subject codes must exist before uploading batches or faculty
- Batches must exist before using "Assign to batches" for faculty
- Duplicate entries are automatically skipped

### Error Handling
- System shows first 10 errors
- Partial success: Some rows may succeed even if others fail
- Check error messages carefully

### Tips
1. **Test with small files first** (2-3 rows)
2. **Verify subject codes** match exactly (case-sensitive)
3. **Use consistent naming** for subject codes
4. **Check results** in respective list views after upload
5. **Use Batch Subjects view** to verify all assignments

---

## Troubleshooting

### "Subject 'XXX' not found"
- Create the subject first using Subject CSV upload

### "At least one subject code is required"
- Faculty CSV must have at least one subject column with a value

### "No batches found in department"
- Create batches first before using "Assign to batches" option

### "section is required"
- Batch CSV must have 'section' column with values

### No mappings created
- Ensure "Assign to batches" is checked for faculty upload
- Verify batches exist in the selected department
- Check that subject codes match exactly

---

## Sample Files Summary

| File | Purpose |
|------|---------|
| `sample_batch_subjects.csv` | Batch-subject assignments (simple format) |
| `sample_batch_subjects_alternative.csv` | Batch-subject assignments (descriptive headers) |
| `sample_faculty_with_subjects.csv` | Faculty with subjects (subject codes as headers) |
| `sample_faculty_alternative.csv` | Faculty with subjects (descriptive headers) |

---

## Additional Documentation

- `BATCH_SUBJECT_CSV_GUIDE.md` - Detailed batch-subject upload guide
- `FACULTY_CSV_GUIDE.md` - Detailed faculty upload guide
- `README.md` - General project documentation
