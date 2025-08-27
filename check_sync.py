import sqlite3

def check_sync_logs():
    try:
        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()
        
        # Check sync logs
        cursor.execute('SELECT * FROM sync_logs ORDER BY sync_time DESC LIMIT 5')
        logs = cursor.fetchall()
        print("Recent sync logs:")
        if logs:
            for log in logs:
                print(f"ID: {log[0]}, Type: {log[1]}, Records: {log[2]}, Status: {log[3]}, Error: {log[4]}, Time: {log[5]}")
        else:
            print("No sync logs found")
        
        # Check attendance logs count
        cursor.execute('SELECT COUNT(*) FROM attendance_logs')
        attendance_count = cursor.fetchone()[0]
        print(f"\nTotal attendance logs: {attendance_count}")
        
        # Check employees count
        cursor.execute('SELECT COUNT(*) FROM employees')
        employees_count = cursor.fetchone()[0]
        print(f"Total employees: {employees_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking sync logs: {e}")

if __name__ == "__main__":
    check_sync_logs()
