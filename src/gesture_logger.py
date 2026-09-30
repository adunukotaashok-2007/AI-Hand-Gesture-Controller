"""
Gesture Logger - Saves gesture history to SQLite database.
"""

import sqlite3
import os


class GestureLogger:
    def __init__(self, db_path="data/gesture_history.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self._connect()
        self._create_table()
        print(f"[GestureLogger] Database ready")

    def _connect(self):
        try:
            self.connection = sqlite3.connect(
                self.db_path, check_same_thread=False)
            self.cursor = self.connection.cursor()
        except sqlite3.Error as e:
            print(f"[GestureLogger] Error: {e}")

    def _create_table(self):
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
            print(f"[GestureLogger] Table error: {e}")

    def log_gesture(self, gesture):
        try:
            self.cursor.execute("""
                INSERT INTO gesture_log
                (gesture_name, action, finger_states, timestamp)
                VALUES (?, ?, ?, ?)
            """, (gesture.name, gesture.action,
                  str(gesture.finger_states),
                  gesture.timestamp.isoformat()))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"[GestureLogger] Log error: {e}")

    def get_gesture_count(self):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM gesture_log")
            r = self.cursor.fetchone()
            return r[0] if r else 0
        except sqlite3.Error:
            return 0

    def get_gesture_statistics(self):
        try:
            self.cursor.execute("""
                SELECT gesture_name, COUNT(*) FROM gesture_log
                GROUP BY gesture_name ORDER BY COUNT(*) DESC
            """)
            return self.cursor.fetchall()
        except sqlite3.Error:
            return []

    def close(self):
        if self.connection:
            self.connection.close()
            print("[GestureLogger] Closed")

    def __del__(self):
        self.close()
