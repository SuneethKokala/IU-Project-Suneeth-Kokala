#!/usr/bin/env python3
import json
import os
from datetime import datetime

# Create test violations
violations = [
    {
        "timestamp": "2025-11-27T08:30:00",
        "employee_id": "EMP001",
        "employee_name": "John Doe",
        "missing_ppe": ["helmet"],
        "notified": False
    },
    {
        "timestamp": "2025-11-27T09:15:00", 
        "employee_id": "EMP002",
        "employee_name": "Jane Smith",
        "missing_ppe": ["vest", "helmet"],
        "notified": False
    }
]

# Create directory and file
os.makedirs('data/logs', exist_ok=True)
with open('data/logs/ppe_violations.log', 'w') as f:
    for violation in violations:
        f.write(json.dumps(violation) + '\n')

print("✅ Test violations created")