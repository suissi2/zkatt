#!/usr/bin/env python3
"""Script to check attendance logs"""

from db_manager import db_manager

def main():
    """Main function to check attendance logs"""
    try:
        logs = db_manager.get_attendance_logs()
        print(f"Total attendance logs in database: {len(logs)}")
        if logs:
            print("Sample log:")
            print(f"Employee ID: {logs[0]['employee_id']}, Time: {logs[0]['datetime']}, Type: {logs[0]['type']}")
    except Exception as e:
        print(f"Error checking attendance logs: {e}")

if __name__ == "__main__":
    main()
