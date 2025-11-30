#!/usr/bin/env python3
import sys
sys.path.append('.')
from app.database import DatabaseManager

def add_employees_table():
    db = DatabaseManager()
    if not db.connected:
        print("❌ Database not connected")
        return
    
    try:
        cursor = db.connection.cursor()
        
        # Create employees table
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
        
        db.connection.commit()
        cursor.close()
        print("✅ Employees table created successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.connection.rollback()

if __name__ == "__main__":
    add_employees_table()