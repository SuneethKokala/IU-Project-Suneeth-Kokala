#!/usr/bin/env python3
"""
Test script for the 10-second violation threshold system
Creates sample violations to test the notification system
"""

import json
import os
from datetime import datetime, timedelta
import time

def create_test_violations():
    """Create test violations for alert system testing"""
    
    # Ensure logs directory exists
    os.makedirs('data/logs', exist_ok=True)
    
    # Sample violations - these represent violations that were continuous for 10+ seconds
    test_violations = [
        {
            "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
            "employee_id": "EMP001",
            "employee_name": "John Smith",
            "missing_ppe": ["helmet", "vest"],
            "location": "Main Camera",
            "notified": True,
            "notified_at": (datetime.now() - timedelta(minutes=3)).isoformat()
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=2)).isoformat(),
            "employee_id": "EMP002", 
            "employee_name": "Sarah Johnson",
            "missing_ppe": ["helmet"],
            "location": "Main Camera",
            "notified": False
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=1)).isoformat(),
            "employee_id": "EMP003",
            "employee_name": "Mike Wilson", 
            "missing_ppe": ["vest"],
            "location": "Main Camera",
            "notified": False
        }
    ]
    
    # Write to log file
    log_file = 'data/logs/ppe_violations.log'
    with open(log_file, 'w') as f:
        for violation in test_violations:
            f.write(json.dumps(violation) + '\n')
    
    print(f"✅ Created {len(test_violations)} test violations")
    print(f"📁 Saved to: {log_file}")
    print("\n📋 Test violations (all were continuous for 10+ seconds):")
    for i, v in enumerate(test_violations, 1):
        status = "✅ Notified" if v['notified'] else "🚨 NEEDS ALERT"
        print(f"{i}. {v['employee_name']} - Missing: {', '.join(v['missing_ppe'])} - {status}")
    
    print(f"\n🎯 How the 10-second system works:")
    print(f"1. Camera detects missing PPE")
    print(f"2. Starts 10-second timer")
    print(f"3. If PPE still missing after 10s → Creates violation & alert")
    print(f"4. If PPE detected before 10s → No violation logged")
    
    print(f"\n🚀 Commands to test:")
    print(f"python3 run.py dashboard  # See alerts")
    print(f"python3 run.py camera     # Test live detection")

def add_new_violation():
    """Add a new violation for real-time testing (simulates 10+ second continuous violation)"""
    
    new_violation = {
        "timestamp": datetime.now().isoformat(),
        "employee_id": f"EMP{int(time.time()) % 1000:03d}",
        "employee_name": "Test Employee",
        "missing_ppe": ["helmet"],
        "location": "Main Camera",
        "notified": False
    }
    
    log_file = 'data/logs/ppe_violations.log'
    with open(log_file, 'a') as f:
        f.write(json.dumps(new_violation) + '\n')
    
    print(f"🚨 Added new violation (continuous 10+ seconds): {new_violation['employee_name']} ({new_violation['employee_id']})")
    print(f"💡 This violation will trigger an alert in the dashboard")
    return new_violation

def simulate_camera_detection():
    """Simulate the camera detection process with 10-second threshold"""
    print("🎬 Simulating camera detection with 10-second threshold...")
    print("\n📹 Camera starts monitoring...")
    
    # Simulate detection phases
    phases = [
        ("✅ PPE detected - all good", 3),
        ("⚠️ Missing helmet detected - starting timer (0s)", 1),
        ("⚠️ Still missing helmet (3s/10s)", 3),
        ("⚠️ Still missing helmet (6s/10s)", 3),
        ("⚠️ Still missing helmet (9s/10s)", 1),
        ("🚨 VIOLATION! Missing helmet for 10+ seconds - ALERT SENT!", 0)
    ]
    
    for message, wait_time in phases:
        print(f"   {message}")
        if wait_time > 0:
            time.sleep(wait_time)
    
    # Add the violation to log
    add_new_violation()
    print("\n✅ Simulation complete. Check dashboard for alert!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "add":
            add_new_violation()
        elif sys.argv[1] == "simulate":
            simulate_camera_detection()
        else:
            print("Usage: python3 test_alert_system.py [add|simulate]")
    else:
        create_test_violations()