#!/usr/bin/env python3
import sys
sys.path.append('.')
from app.database import DatabaseManager

def check_tables():
    db = DatabaseManager()
    if not db.connected:
        print("❌ Database not connected")
        return
    
    try:
        cursor = db.connection.cursor()
        
        # List all tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        print("📋 Database Tables:")
        for table in tables:
            print(f"  • {table[0]}")
            
            # Show table structure
            cursor.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table[0]}'
            """)
            columns = cursor.fetchall()
            for col in columns:
                print(f"    - {col[0]} ({col[1]})")
            
            # Show row count
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"    Rows: {count}\n")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_tables()