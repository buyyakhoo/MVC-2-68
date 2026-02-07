import sqlite3
from typing import List, Tuple, Optional

class SubjectsModel:
    """
    SQLite-backed model for Subjects table.
    """

    def __init__(self, db_path: str = "src/database/school_registration.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

    def get_all_subjects(self) -> List[Tuple]:
        """Get all subjects data"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT SubjectID, SubjectName, Credits, Instructor, PrerequisiteSubjectID 
            FROM Subjects
            ORDER BY SubjectID
        """)
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_subject_by_id(self, subject_id) -> Optional[Tuple]:
        """Get specific subject by ID"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT SubjectID, SubjectName, Credits, Instructor, PrerequisiteSubjectID 
            FROM Subjects 
            WHERE SubjectID = ?
        """, (str(subject_id),))  # เปลี่ยนเป็น str เพราะ SubjectID เป็น TEXT
        result = cursor.fetchone()
        cursor.close()
        return result

    def get_subjects_by_type(self, subject_type: str) -> List[Tuple]:
        """Get subjects by type (faculty/general)"""
        cursor = self.conn.cursor()
        if subject_type == "faculty":
            cursor.execute("""
                SELECT SubjectID, SubjectName, Credits, Instructor, PrerequisiteSubjectID 
                FROM Subjects 
                WHERE SubjectID LIKE '0550%'
                ORDER BY SubjectID
            """)
        elif subject_type == "general":
            cursor.execute("""
                SELECT SubjectID, SubjectName, Credits, Instructor, PrerequisiteSubjectID 
                FROM Subjects 
                WHERE SubjectID LIKE '9069%'
                ORDER BY SubjectID
            """)
        else:
            return []
        
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_subjects_with_prerequisites(self) -> List[Tuple]:
        """Get subjects that have prerequisites"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT SubjectID, SubjectName, Credits, Instructor, PrerequisiteSubjectID 
            FROM Subjects 
            WHERE PrerequisiteSubjectID IS NOT NULL
            ORDER BY SubjectID
        """)
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_subjects_by_instructor(self, instructor_name: str) -> List[Tuple]:
        """Get subjects taught by specific instructor"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT SubjectID, SubjectName, Credits, Instructor, PrerequisiteSubjectID 
            FROM Subjects 
            WHERE Instructor LIKE ?
            ORDER BY SubjectID
        """, (f"%{instructor_name}%",))
        result = cursor.fetchall()
        cursor.close()
        return result

    def search_subjects(self, search_term: str) -> List[Tuple]:
        """Search subjects by name or ID"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT SubjectID, SubjectName, Credits, Instructor, PrerequisiteSubjectID 
            FROM Subjects 
            WHERE SubjectName LIKE ? OR SubjectID LIKE ?
            ORDER BY SubjectID
        """, (f"%{search_term}%", f"%{search_term}%"))  # ไม่ต้อง CAST เป็น TEXT แล้ว
        result = cursor.fetchall()
        cursor.close()
        return result

    def close_connection(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()