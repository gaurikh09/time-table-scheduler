# Batch-Subject CSV Upload Feature

## Overview
This feature allows you to bulk create batches and assign subjects to them using a CSV file. This is much faster than manually creating each batch and assigning subjects one by one.

## How to Use

### Step 1: Prepare Your CSV File
Create a CSV file with the following format:

**Required Column:**
- `section` - The section name/code (e.g., 2EA1, 2EB1, etc.)

**Subject Columns:**
- ALL other columns (except 'section') will be treated as subject codes
- Column names can be ANYTHING - they are ignored, only the values matter
- You can use: `subject1`, `subject-code1`, `CS101`, or any name you prefer
- Empty cells are automatically ignored

**Example CSV Format 1 (Simple):**
```csv
section,CS101,CS102,CS103,CS104,CS105
2EA1,CS101,CS102,CS103,CS104,CS105
2EA2,CS101,CS102,CS103,CS104,CS105
2EB1,CS101,CS102,CS103,CS106,CS107
```

**Example CSV Format 2 (Descriptive Headers):**
```csv
section,subject-code1,subject-code2,subject-code3,subject-code4,subject-code5
2EA1,CS101,CS102,CS103,CS104,CS105
2EA2,CS101,CS102,CS103,CS104,CS105
2EB1,CS101,CS102,CS103,CS106,CS107
```

**Example CSV Format 3 (Mixed - with empty cells):**
```csv
section,sub1,sub2,sub3,sub4,sub5,sub6
2EA1,CS101,CS102,CS103,CS104,CS105,
2EA2,CS101,CS102,CS103,CS104,,
2EB1,CS101,CS102,CS103,,,
```

### Step 2: Access the Upload Page
1. Navigate to **Batches** page from the dashboard
2. Click the **Upload CSV** button in the top right corner

### Step 3: Fill the Form
You need to provide:
- **Department**: Select the department for all batches
- **Year**: Enter the year (1-4)
- **Semester**: Enter the semester (1-8)
- **CSV File**: Upload your prepared CSV file

### Step 4: Upload and Process
- Click **Upload CSV** button
- The system will:
  - Create batches if they don't exist (with default strength=60, max_classes_per_day=6)
  - Link subjects to batches based on the subject codes
  - Skip duplicate batch-subject links
  - Report any errors (e.g., subject not found)

## Important Notes

1. **Subjects Must Exist First**: All subject codes in your CSV must already exist in the system. Create subjects first using:
   - Manual creation via "Add Subject" button
   - Subject CSV upload feature

2. **Batch Creation**: If a batch doesn't exist, it will be created with default values:
   - Strength: 60 students
   - Max classes per day: 6
   - You can edit these values later

3. **Duplicate Handling**: 
   - If a batch already exists, it will be updated with new subjects
   - Duplicate batch-subject links are automatically skipped

4. **Error Handling**: The system will report:
   - Missing required fields
   - Subject codes that don't exist
   - Any processing errors

## Example Workflow

### Complete Setup Process:

1. **Create Subjects First** (via Subject CSV or manual):
   ```csv
   subject-code,subject-name,weekly-frequency
   CS101,Data Structures,4
   CS102,Algorithms,4
   CS103,Database Systems,3
   CS104,Operating Systems,4
   CS105,Computer Networks,3
   ```

2. **Upload Batch-Subject CSV**:
   - Department: Computer Science
   - Year: 2
   - Semester: 3
   - CSV: Upload your batch-subjects file

3. **Result**: All batches created with subjects assigned!

## Sample Files Included

- `sample_batch_subjects.csv` - Example batch-subject CSV file

## Troubleshooting

**Error: "Subject [CODE] not found"**
- Solution: Create the subject first before uploading the batch CSV

**Error: "section is required"**
- Solution: Ensure your CSV has a 'section' column with values

**Batches created but no subjects linked**
- Solution: Check that your CSV has subject-code columns (subject-code1, subject-code2, etc.)
- Ensure subject codes are correct and exist in the system
