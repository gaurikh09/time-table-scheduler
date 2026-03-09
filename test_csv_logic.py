# Test CSV Processing Logic
# This demonstrates how the faculty CSV upload processes multiple subjects

import csv
import io

# Sample CSV content
csv_content = """Teach-name,Emp-ID,email,CS101,CS102,CS103,CS104,CS105
Dr. John Smith,EMP001,john@edu,CS101,CS102,CS103,CS104,CS105
Dr. Jane Doe,EMP002,jane@edu,CS101,CS102,CS103,,
"""

# Parse CSV
io_string = io.StringIO(csv_content)
reader = csv.DictReader(io_string)

for idx, row in enumerate(reader, start=2):
    teacher_name = row.get('Teach-name', '').strip()
    employee_id = row.get('Emp-ID', '').strip()
    email = row.get('email', '').strip()
    
    # Extract subject codes from remaining columns
    subject_codes = []
    for key, value in row.items():
        if key.lower() not in ['teach-name', 'emp-id', 'email'] and value and value.strip():
            subject_codes.append(value.strip())
    
    print(f"Row {idx}: {teacher_name} ({employee_id})")
    print(f"  Email: {email}")
    print(f"  Subjects found: {len(subject_codes)}")
    print(f"  Subject codes: {subject_codes}")
    print()

# Expected output:
# Row 2: Dr. John Smith (EMP001)
#   Email: john@edu
#   Subjects found: 5
#   Subject codes: ['CS101', 'CS102', 'CS103', 'CS104', 'CS105']
#
# Row 3: Dr. Jane Doe (EMP002)
#   Email: jane@edu
#   Subjects found: 3
#   Subject codes: ['CS101', 'CS102', 'CS103']
