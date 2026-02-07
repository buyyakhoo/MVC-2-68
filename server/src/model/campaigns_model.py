import sqlite3
from typing import List, Optional

class CampaignsModel:
    """
    Model for Campaigns table.
    """
    
    def __init__(self, db_path: str = "src/database/political_party.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def get_campaigns_by_politician(self, politician_id: str) -> List[dict]:
        """Get all campaigns history for a specific politician"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM Campaigns 
            WHERE politician_id = ? 
            ORDER BY election_year DESC
        """, (politician_id,))
        result = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        return result

    def get_campaign_by_id(self, campaign_id: str) -> Optional[dict]:
        """Get specific campaign details"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Campaigns WHERE campaign_id = ?", (campaign_id,))
        row = cursor.fetchone()
        cursor.close()
        return dict(row) if row else None

    def close_connection(self):
        if self.conn:
            self.conn.close()