import sqlite3
from typing import List

class PromiseUpdatesModel:
    """
    Model for PromiseUpdates table.
    """
    
    def __init__(self, db_path: str = "src/database/political_party.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def get_updates_by_promise_id(self, promise_id: str) -> List[dict]:
        """[View 2 History] Get all updates for a specific promise"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT update_id, update_date, detail
            FROM PromiseUpdates
            WHERE promise_id = ?
            ORDER BY update_date DESC
        """, (promise_id,))
        result = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return result

    def add_update(self, promise_id: str, detail: str, update_date: str) -> bool:
        """[View 3] Add new progress update"""
        try:
            cursor = self.conn.cursor()
            
            # Auto-generate ID logic (Uxxx -> U+1)
            cursor.execute("SELECT MAX(update_id) FROM PromiseUpdates")
            max_id = cursor.fetchone()[0]
            
            if max_id:
                # Assuming ID format "Uxxx" e.g., "U005"
                prefix = max_id[0]
                try:
                    number = int(max_id[1:]) + 1
                except ValueError:
                    number = 1 # Fallback if ID format is weird
                new_id = f"{prefix}{number:03d}"
            else:
                new_id = "U001"

            cursor.execute("""
                INSERT INTO PromiseUpdates (update_id, promise_id, update_date, detail)
                VALUES (?, ?, ?, ?)
            """, (new_id, promise_id, update_date, detail))
            
            self.conn.commit()
            cursor.close()
            return True
        except sqlite3.Error as e:
            print(f"Error adding update: {e}")
            return False

    def close_connection(self):
        if self.conn:
            self.conn.close()