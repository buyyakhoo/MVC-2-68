import sqlite3
from typing import List, Tuple, Optional, Dict

class PoliticiansModel:
    """
    Model for Politicians table.
    """
    
    def __init__(self, db_path: str = "src/database/political_party.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # ให้ผลลัพธ์เป็น Dictionary-like

    def get_all_politicians(self) -> List[dict]:
        """Get all politicians ordered by name"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Politicians ORDER BY name")
        result = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return result

    def get_politician_by_id(self, politician_id: str) -> Optional[dict]:
        """Get specific politician profile"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Politicians WHERE politician_id = ?", (politician_id,))
        row = cursor.fetchone()
        cursor.close()
        return dict(row) if row else None
    
    def get_politicians_by_party(self, party_name: str) -> List[dict]:
        """Filter politicians by party"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Politicians WHERE party = ?", (party_name,))
        result = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return result

    def close_connection(self):
        if self.conn:
            self.conn.close()