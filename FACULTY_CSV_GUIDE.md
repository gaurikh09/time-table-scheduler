# Faculty CSV Upload with Subject Assignment

## Overview
Upload faculty members and their teachable subjects in bulk using a CSV file. This feature allows you to:
1. Create multiple faculty members at once
2. Specify which subjects each faculty can teach
3. Optionally auto-assign faculty to teach subjects for all batches in the department

## CSV Format

### Required Columns
- **Teach-name**: Full name of the faculty member (e.g., "Dr. John Smith")
- **Emp-ID**: Unique employee ID (e.g., "EMP001")
- **At least one subject code column**: Faculty MUST have at least one subject they can teach

### Optional Columns
- **email**: Faculty email address (can be empty)

### Subject Columns (REQUIRED)
- **At least one subject column is MANDATORY**
- All columns (except Teach-name, Emp-ID, email) are treated as subject codes
- Column names can be anything - only the values matter
- Empty cells are ignored, but each faculty must have at least one subject

### Example Format 1 (Subject codes as headers)
```csv
Teach-name,Emp-ID,email,CS101,CS102,CS103
Dr. John Smith,EMP001,john.smith@university.edu,CS101,CS102,
Dr. Jane Doe,EMP002,jane.doe@university.edu,CS102,CS103,
Prof. Robert Brown,EMP003,robert.brown@university.edu,CS101,CS103,
```

### Example Format 2 (Descriptive headers)
```csv
Teach-name,Emp-ID,email,subject1,subject2,subject3,subject4
Dr. John Smith,EMP001,john.smith@university.edu,CS101,CS102,CS103,
Dr. Jane Doe,EMP002,jane.doe@university.edu,CS102,CS103,CS104,
Prof. Robert Brown,EMP003,robert.brown@university.edu,CS101,CS103,CS105,
```

## How to Use

### Step 1: Prepare Your CSV File
1. Create a CSV file with the required columns
2. Add subject codes in additional columns
3. Leave cells empty if a faculty doesn't teach that subject
4. Subject codes must match existing subjects in the system

### Step 2: Upload the CSV
1. Navigate to **Faculty** page
2. Click **Upload CSV** button
3. Select your department
4. Choose your CSV file
5. **Optional**: Check "Assign subjects to all batches in department"

### Step 3: Understand the Options

#### Option A: Without "Assign to batches" (Default)
- Creates faculty members
- Records which subjects they can teach
- Does NOT create faculty-subject-batch mappings
- You'll need to manually assign faculty to specific batches later

#### Option B: With "Assign to batches" (Checked)
- Creates faculty members
- Automatically creates faculty-subject-batch mappings for ALL batches in the department
- Faculty will be assigned to teach their subjects for every batch
- Useful when faculty teach the same subjects across all batches

## Important Notes

1. **Subjects Must Exist First**: All subject codes in your CSV must already exist in the system
   - Create subjects first using Subject CSV upload or manual creation

2. **Batches Must Exist**: If using "Assign to batches", batches must already be created
   - Create batches first using Batch CSV upload or manual creation

3. **Duplicate Handling**: 
   - Faculty with existing Emp-ID will be skipped
   - Subject assignments are only created if they don't already exist

4. **Empty Cells**: Empty subject cells are automatically ignored

## Complete Workflow Example

### Step 1: Create Subjects
Upload subjects CSV:
```csv
subject-code,subject-name,weekly-frequency
CS101,Data Structures,4
CS102,Algorithms,4
CS103,Database Systems,3
CS104,Operating Systems,4
CS105,Computer Networks,3
```

### Step 2: Create Batches
Upload batch-subject CSV:
```csv
section,CS101,CS102,CS103,CS104,CS105
2EA1,CS101,CS102,CS103,CS104,CS105
2EA2,CS101,CS102,CS103,CS104,CS105
2EB1,CS101,CS102,CS103,CS104,CS105
```

### Step 3: Upload Faculty with Subjects
Upload faculty CSV with "Assign to batches" checked:
```csv
Teach-name,Emp-ID,email,CS101,CS102,CS103
Dr. John Smith,EMP001,john@edu,CS101,CS102,
Dr. Jane Doe,EMP002,jane@edu,CS102,CS103,
```

**Result**: 
- 2 faculty members created
- Dr. John Smith assigned to teach CS101 and CS102 for all 3 batches (6 mappings)
- Dr. Jane Doe assigned to teach CS102 and CS103 for all 3 batches (6 mappings)
- Total: 12 faculty-subject-batch mappings created automatically

## Troubleshooting

### Error: "Subject 'XXX' not found"
**Solution**: Create the subject first before uploading faculty CSV

### Error: "Teach-name is required"
**Solution**: Ensure every row has a faculty name in the Teach-name column

### Error: "Emp-ID is required"
**Solution**: Ensure every row has an employee ID in the Emp-ID column

### No subject assignments created
**Solution**: 
- Check that subject codes in CSV match existing subjects exactly (case-sensitive)
- Ensure "Assign to batches" is checked if you want automatic batch assignments
- Verify that batches exist in the selected department

## Sample Files Included

- `sample_faculty_with_subjects.csv` - Faculty with subject codes as headers
- `sample_faculty_alternative.csv` - Faculty with descriptive column headers

## Tips

1. **Start Small**: Test with 2-3 faculty members first
2. **Check Subjects**: Verify all subject codes exist before uploading
3. **Use Batch Assignment Wisely**: Only check "Assign to batches" if faculty teach ALL batches
4. **Manual Fine-tuning**: You can always adjust individual assignments later in the Mappings section
