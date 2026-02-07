import sqlite3
from typing import List, Optional

class PromisesModel:
    """
    Model for Promises table.
    """
    
    def __init__(self, db_path: str = "src/database/political_party.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def get_all_promises_with_politician_info(self) -> List[dict]:
        """
        [View 1] Get all promises joined with politician name.
        Ordered by announcement date (Newest first).
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                p.promise_id, p.description, p.status, p.announcement_date,
                pol.name AS politician_name, 
                pol.party AS party_name,
                pol.politician_id
            FROM Promises p
            JOIN Politicians pol ON p.politician_id = pol.politician_id
            ORDER BY p.announcement_date DESC
        """)
        result = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return result

    def get_promises_by_politician(self, politician_id: str) -> List[dict]:
        """[View 4] Get promises for specific politician"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM Promises 
            WHERE politician_id = ? 
            ORDER BY announcement_date DESC
        """, (politician_id,))
        result = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return result

    def get_promise_detail_by_id(self, promise_id: str) -> Optional[dict]:
        """[View 2 Header] Get detailed promise info including politician name"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.*, pol.name AS politician_name, pol.party
            FROM Promises p
            JOIN Politicians pol ON p.politician_id = pol.politician_id
            WHERE p.promise_id = ?
        """, (promise_id,))
        row = cursor.fetchone()
        cursor.close()
        return dict(row) if row else None

    def update_promise_status(self, promise_id: str, new_status: str) -> bool:
        """Update the status of a promise"""
        valid_statuses = {"ยังไม่เริ่ม", "กำลังดำเนินการ", "เงียบหาย", "สำเร็จแล้ว"}
        if new_status not in valid_statuses:
            return False

        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Promises SET status = ? WHERE promise_id = ?", (new_status, promise_id))
            self.conn.commit()
            cursor.close()
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def close_connection(self):
        if self.conn:
            self.conn.close()