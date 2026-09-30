"""
Gesture Logger Module
=====================
Logs recognized gestures to a SQLite database for history tracking.

Why this is a separate class:
- Database operations are isolated from main logic
- Easy to switch database (SQLite → MySQL) without changing other code
- Follows Single Responsibility Principle
- Demonstrates: Database usage, Encapsulation

SQLite was chosen because:
- Built into Python (no installation needed)
- File-based (no server setup)
- Perfect for a college mini-project
- Easy to demonstrate during presentation
"""

import sqlite3
import os
from datetime import datetime


class GestureLogger:
    """
    Logs gesture detections to a SQLite database.

    Attributes:
        db_path (str): Path to the SQLite database file
        connection: SQLite database connection
        cursor: SQLite cursor for executing queries
    """

    def __init__(self, db_path="data/gesture_history.db"):
        """
        Initialize the database connection and create tables.

        Args:
            db_path (str): Where to store the database file

        What happens:
        1. Create the 'data' directory if it doesn't exist
        2. Connect to SQLite (creates file if it doesn't exist)
        3. Create the gestures table if it doesn't exist
        """
        # Create directory if needed
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.db_path = db_path
        self.connection = None
        self.cursor = None

        self._connect()
        self._create_table()

        print(f"[GestureLogger] Database ready at {db_path}")

    def _connect(self):
        """
        Establish connection to SQLite database.

        check_same_thread=False allows the database to be used
        from different threads (needed for some setups).
        """
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            self.cursor = self.connection.cursor()
        except sqlite3.Error as e:
            print(f"[GestureLogger] Database connection error: {e}")

    def _create_table(self):
        """
        Create the gestures table if it doesn't exist.

        Table structure:
        - id: Auto-incrementing primary key
        - gesture_name: Name of the detected gesture
        - action: What action was triggered
        - finger_states: Which fingers were up/down
        - timestamp: When the gesture was detected
        """
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS gesture_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gesture_name TEXT NOT NULL,
                    action TEXT,
                    finger_states TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"[GestureLogger] Table creation error: {e}")

    def log_gesture(self, gesture):
        """
        Save a detected gesture to the database.

        Args:
            gesture (Gesture): The gesture object to log

        Why log gestures?
        - Track usage patterns
        - Debug gesture recognition issues
        - Show during project presentation
        - Demonstrate database knowledge
        """
        try:
            self.cursor.execute("""
                INSERT INTO gesture_log
                    (gesture_name, action, finger_states, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                gesture.name,
                gesture.action,
                str(gesture.finger_states),
                gesture.timestamp.isoformat()
            ))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"[GestureLogger] Logging error: {e}")

    def get_recent_gestures(self, limit=10):
        """
        Retrieve the most recent gesture entries.

        Args:
            limit (int): How many entries to retrieve

        Returns:
            list: List of tuples (id, name, action, fingers, timestamp)
        """
        try:
            self.cursor.execute("""
                SELECT * FROM gesture_log
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[GestureLogger] Query error: {e}")
            return []

    def get_gesture_count(self):
        """
        Get total number of logged gestures.

        Returns:
            int: Total count of logged gestures
        """
        try:
            self.cursor.execute("SELECT COUNT(*) FROM gesture_log")
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"[GestureLogger] Count error: {e}")
            return 0

    def get_gesture_statistics(self):
        """
        Get count of each gesture type.

        Returns:
            list: List of (gesture_name, count) tuples

        Useful for presentation: "Thumbs Up was used 45 times!"
        """
        try:
            self.cursor.execute("""
                SELECT gesture_name, COUNT(*) as count
                FROM gesture_log
                GROUP BY gesture_name
                ORDER BY count DESC
            """)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[GestureLogger] Statistics error: {e}")
            return []

    def clear_history(self):
        """Delete all logged gestures."""
        try:
            self.cursor.execute("DELETE FROM gesture_log")
            self.connection.commit()
            print("[GestureLogger] History cleared")
        except sqlite3.Error as e:
            print(f"[GestureLogger] Clear error: {e}")

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            print("[GestureLogger] Database closed")

    def __del__(self):
        """Destructor to ensure database is closed."""
        self.close()
