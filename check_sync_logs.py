#!/usr/bin/env python3
"""Script to check synchronization logs"""

from db_manager import db_manager

def main():
    """Main function to check sync logs"""
    try:
        logs = db_manager.get_sync_logs()
        print(f"Total sync logs: {len(logs)}")
        print("\nLast 5 sync logs:")
        for log in logs[-5:]:
            print(f"Type: {log['sync_type']}, Count: {log['records_count']}, Status: {log['status']}, Timestamp: {log['sync_time']}")
    except Exception as e:
        print(f"Error checking sync logs: {e}")

if __name__ == "__main__":
    main()
