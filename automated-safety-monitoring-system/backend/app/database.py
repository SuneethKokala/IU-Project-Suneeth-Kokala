import psycopg2
import json
from datetime import datetime
from config.settings import DATABASE_HOST, DATABASE_PORT, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD

class DatabaseManager:
    def __init__(self):
        self.connected = False
        self.connection = None
        self.connect()
        if self.connected:
            self.create_tables()
    
    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                database=DATABASE_NAME,
                user=DATABASE_USER,
                password=DATABASE_PASSWORD
            )
            self.connected = True
            print("✅ Database connected")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            self.connected = False
    
    def create_tables(self):
        try:
            cursor = self.connection.cursor()
            
            # Employees table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id SERIAL PRIMARY KEY,
                    employee_id VARCHAR(50) UNIQUE,
                    name VARCHAR(100),
                    department VARCHAR(50),
                    position VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # PPE violations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ppe_violations (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    employee_id VARCHAR(50),
                    employee_name VARCHAR(100),
                    missing_ppe TEXT,
                    location VARCHAR(100) DEFAULT 'Main Camera',
                    notified BOOLEAN DEFAULT FALSE
                )
            """)
            
            self.connection.commit()
            cursor.close()
        except Exception as e:
            print(f"❌ Table creation failed: {e}")
    
    def log_violation(self, employee_id, employee_name, missing_ppe, location="Main Camera"):
        if not self.connected:
            return False
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO ppe_violations (employee_id, employee_name, missing_ppe, location)
                VALUES (%s, %s, %s, %s)
            """, (employee_id, employee_name, json.dumps(missing_ppe), location))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"❌ Failed to log violation: {e}")
            return False
    
    def get_violations(self):
        if not self.connected:
            return []
        try:
            # Rollback any failed transaction
            self.connection.rollback()
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM ppe_violations ORDER BY timestamp DESC")
            violations = cursor.fetchall()
            cursor.close()
            
            result = []
            for v in violations:
                result.append({
                    'id': v[0],
                    'timestamp': v[1].isoformat(),
                    'employee_id': v[2],
                    'employee_name': v[3],
                    'missing_ppe': json.loads(v[4]) if v[4] else [],
                    'location': v[5],
                    'notified': v[6]
                })
            return result
        except Exception as e:
            print(f"❌ Failed to get violations: {e}")
            self.connection.rollback()
            return []
    

    
    def clear_violations(self):
        if not self.connected:
            return False
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM ppe_violations")
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"❌ Failed to clear violations: {e}")
            return False
    
    def add_employee(self, employee_id, name, department, position):
        if not self.connected:
            return False
        try:
            # Rollback any failed transaction
            self.connection.rollback()
            
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO employees (id, name, department)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (employee_id, name, department))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"❌ Failed to add employee: {e}")
            self.connection.rollback()
            return False
    
    def get_employees(self):
        if not self.connected:
            return []
        try:
            # Rollback any failed transaction
            self.connection.rollback()
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM employees ORDER BY name")
            employees = cursor.fetchall()
            cursor.close()
            
            result = []
            for emp in employees:
                result.append({
                    'employee_id': emp[0],
                    'name': emp[1],
                    'department': emp[2] if len(emp) > 2 else 'N/A',
                    'position': 'Employee',
                    'created_at': emp[3].isoformat() if len(emp) > 3 and emp[3] else None
                })
            return result
        except Exception as e:
            print(f"❌ Failed to get employees: {e}")
            self.connection.rollback()
            return []
    
    def delete_employee(self, employee_id):
        if not self.connected:
            return False
        try:
            self.connection.rollback()
            
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"❌ Failed to delete employee: {e}")
            self.connection.rollback()
            return False
    
    def mark_violation_notified(self, violation_id):
        if not self.connected:
            return False
        try:
            self.connection.rollback()
            
            cursor = self.connection.cursor()
            cursor.execute("UPDATE ppe_violations SET notified = TRUE WHERE id = %s", (violation_id,))
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"❌ Failed to mark violation as notified: {e}")
            self.connection.rollback()
            return False
    
    def update_violation_notification(self, timestamp, notified_status):
        """Update notification status by timestamp"""
        if not self.connected:
            return False
        try:
            self.connection.rollback()
            
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE ppe_violations SET notified = %s WHERE timestamp = %s", 
                (notified_status, timestamp)
            )
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"❌ Failed to update violation notification: {e}")
            self.connection.rollback()
            return False