import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional

class StudentsModel:
    """
    SQLite-backed model for Students table.
    """

    def __init__(self, db_path: str = "src/database/school_registration.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

    def get_all_students(self) -> List[Tuple]:
        """Get all students data"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT StudentID, Title, FirstName, LastName, BirthDate, 
                   CurrentSchool, Email, CurriculumID 
            FROM Students
            ORDER BY FirstName, LastName
        """)
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_student_by_id(self, student_id) -> Optional[Tuple]:
        """Get specific student by ID"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT StudentID, Title, FirstName, LastName, BirthDate, 
                   CurrentSchool, Email, CurriculumID 
            FROM Students 
            WHERE StudentID = ?
        """, (int(student_id),))
        result = cursor.fetchone()
        cursor.close()
        return result

    def get_students_by_curriculum(self, curriculum_id) -> List[Tuple]:
        """Get students by curriculum ID"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT StudentID, Title, FirstName, LastName, BirthDate, 
                   CurrentSchool, Email, CurriculumID 
            FROM Students 
            WHERE CurriculumID = ?
            ORDER BY FirstName, LastName
        """, (int(curriculum_id),))
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_students_by_school(self, school_name: str) -> List[Tuple]:
        """Get students by school name (for filtering)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT StudentID, Title, FirstName, LastName, BirthDate, 
                   CurrentSchool, Email, CurriculumID 
            FROM Students 
            WHERE CurrentSchool LIKE ?
            ORDER BY FirstName, LastName
        """, (f"%{school_name}%",))
        result = cursor.fetchall()
        cursor.close()
        return result

    def search_students(self, search_term: str) -> List[Tuple]:
        """Search students by name or ID"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT StudentID, Title, FirstName, LastName, BirthDate, 
                   CurrentSchool, Email, CurriculumID 
            FROM Students 
            WHERE FirstName LIKE ? OR LastName LIKE ? OR 
                  CAST(StudentID AS TEXT) LIKE ?
            ORDER BY FirstName, LastName
        """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_student_age(self, student_id) -> Optional[int]:
        """Calculate student age from birth date"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT BirthDate FROM Students WHERE StudentID = ?", (int(student_id),))
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            return None
        
        try:
            birth_date = datetime.strptime(result[0], "%Y-%m-%d")
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age
        except ValueError:
            return None

    def is_student_eligible(self, student_id) -> bool:
        """Check if student is eligible (age >= 15)"""
        age = self.get_student_age(student_id)
        return age is not None and age >= 15

    def get_unique_schools(self) -> List[str]:
        """Get list of unique schools for filtering"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT CurrentSchool FROM Students ORDER BY CurrentSchool")
        result = cursor.fetchall()
        cursor.close()
        return [row[0] for row in result]

    def get_students_sorted_by_name(self) -> List[Tuple]:
        """Get students sorted by name"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT StudentID, Title, FirstName, LastName, BirthDate, 
                   CurrentSchool, Email, CurriculumID 
            FROM Students 
            ORDER BY FirstName, LastName
        """)
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_students_sorted_by_age(self) -> List[Tuple]:
        """Get students sorted by age (birth date)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT StudentID, Title, FirstName, LastName, BirthDate, 
                   CurrentSchool, Email, CurriculumID 
            FROM Students 
            ORDER BY BirthDate DESC
        """)
        result = cursor.fetchall()
        cursor.close()
        return result

    def add_student(self, student_id: int, title: str, first_name: str, 
                   last_name: str, birth_date: str, current_school: str, 
                   email: str, curriculum_id: int) -> bool:
        """Add new student"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO Students (StudentID, Title, FirstName, LastName, 
                                    BirthDate, CurrentSchool, Email, CurriculumID)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (student_id, title, first_name, last_name, birth_date, 
                  current_school, email, curriculum_id))
            self.conn.commit()
            cursor.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def close_connection(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()