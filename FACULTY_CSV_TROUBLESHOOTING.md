# Faculty CSV Upload - Troubleshooting Guide

## Problem: Subjects Not Showing for Faculty Members

### Symptoms
- Faculty members are created successfully
- But subjects don't appear in the faculty list
- Or only 1 subject appears instead of all subjects

### Root Cause
The "Assign to batches" checkbox was NOT checked during CSV upload.

### Solution
**You MUST check the "Assign to batches" checkbox** when uploading faculty CSV for subjects to be stored and displayed.

## Step-by-Step Verification

### Step 1: Verify Prerequisites
Before uploading faculty CSV, ensure:

1. **Subjects exist**: All subject codes in your CSV must already be in the database
   - Go to Subjects page and verify each subject code exists
   - Example: CS101, CS102, CS103, etc.

2. **Batches exist**: At least one batch must exist in the department
   - Go to Batches page and verify batches exist
   - Example: 2EA1, 2EA2, 2EB1, etc.

3. **Department is correct**: Select the correct department that has the batches

### Step 2: Prepare CSV Correctly
Your CSV should have:
```csv
Teach-name,Emp-ID,email,CS101,CS102,CS103,CS104,CS105
Dr. John Smith,EMP001,john@edu,CS101,CS102,CS103,CS104,CS105
Dr. Jane Doe,EMP002,jane@edu,CS101,CS102,CS103,,
```

- Each faculty MUST have at least one subject code
- Empty cells are OK (like CS104 and CS105 for Dr. Jane Doe)
- Column names don't matter (except Teach-name, Emp-ID, email)

### Step 3: Upload with Checkbox CHECKED
1. Go to Faculty → Upload CSV
2. Select Department
3. Choose your CSV file
4. **✅ CHECK the "Assign subjects to all batches" checkbox** ← CRITICAL!
5. Click Upload CSV

### Step 4: Verify Results
After upload, you should see a success message like:
```
Successfully created 2 faculty members, skipped 0 duplicates, 
and created 24 subject-batch assignments. Found 8 subject codes in CSV.
```

**Calculation**: 
- Dr. John Smith: 5 subjects × 3 batches = 15 mappings
- Dr. Jane Doe: 3 subjects × 3 batches = 9 mappings
- Total: 24 mappings

### Step 5: Check Faculty List
1. Go to Faculty page
2. You should see ALL subjects listed for each faculty member
3. Example: Dr. John Smith should show: CS101, CS102, CS103, CS104, CS105

### Step 6: Check Faculty Detail
1. Click "View" button for a faculty member
2. You should see all subjects with their assigned batches
3. Example: CS101 → Teaching to 3 batches (2EA1, 2EA2, 2EB1)

## Common Errors and Solutions

### Error: "No batches found in department"
**Solution**: Create batches first before uploading faculty CSV

### Error: "Subject 'CS101' not found"
**Solution**: Create the subject first using Subject CSV upload or manual creation

### Warning: "Found X subject codes but NO assignments were created"
**Solution**: You forgot to check the "Assign to batches" checkbox. Re-upload with checkbox checked.

### Only 1 subject showing instead of 5
**Possible causes**:
1. Checkbox was not checked → Re-upload with checkbox checked
2. Only 1 subject exists in database → Create all subjects first
3. Subject codes in CSV don't match database → Verify exact spelling and case

## How It Works

When "Assign to batches" is checked:
1. System reads each row in CSV
2. Extracts ALL subject codes from columns (except Teach-name, Emp-ID, email)
3. For EACH subject code:
   - Finds the subject in database
   - For EACH batch in the department:
     - Creates a FacultySubject mapping (faculty + subject + batch)

Example:
- 1 faculty with 5 subjects
- Department has 3 batches
- Result: 5 × 3 = 15 FacultySubject mappings created

## Testing

Use the test script to verify CSV parsing:
```bash
python test_csv_logic.py
```

This will show how many subjects are extracted from each row.

## Still Having Issues?

1. Check the success/error message after upload
2. Go to Mappings page to see all FacultySubject records
3. Verify in Faculty Detail page (click View button)
4. Check that batches exist and have subjects assigned
5. Ensure all subject codes match exactly (case-sensitive)
