import sqlite3

def check_database_structure():
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = cursor.fetchall()
        print("Tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check each table structure
        for table in tables:
            table_name = table[0]
            print(f"\nStructure of table '{table_name}':")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for column in columns:
                print(f"  - {column[1]} ({column[2]})")
        
        conn.close()
        print("\nDatabase check completed successfully!")
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_database_structure()
