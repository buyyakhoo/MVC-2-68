import sqlite3
from typing import List, Tuple, Optional

class SubjectStructureModel:
    """
    SQLite-backed model for SubjectStructure table.
    """

    def __init__(self, db_path: str = "src/database/school_registration.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

    def get_all_curriculum_structures(self) -> List[Tuple]:
        """Get all curriculum structure data"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT CurriculumID, CurriculumName, FacultyName, SubjectID, Semester 
            FROM SubjectStructure
            ORDER BY CurriculumID, Semester, SubjectID
        """)
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_curriculum_by_id(self, curriculum_id) -> List[Tuple]:
        """Get curriculum structure by curriculum ID"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT CurriculumID, CurriculumName, FacultyName, SubjectID, Semester 
            FROM SubjectStructure 
            WHERE CurriculumID = ?
            ORDER BY Semester, SubjectID
        """, (int(curriculum_id),))
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_subjects_by_curriculum_and_semester(self, curriculum_id, semester) -> List[Tuple]:
        """Get subjects for specific curriculum and semester"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT ss.CurriculumID, ss.CurriculumName, ss.FacultyName, 
                   ss.SubjectID, ss.Semester, s.SubjectName, s.Credits
            FROM SubjectStructure ss
            LEFT JOIN Subjects s ON ss.SubjectID = s.SubjectID
            WHERE ss.CurriculumID = ? AND ss.Semester = ?
            ORDER BY ss.SubjectID
        """, (int(curriculum_id), int(semester)))
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_available_curriculums(self) -> List[Tuple]:
        """Get unique list of curriculums"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT CurriculumID, CurriculumName, FacultyName 
            FROM SubjectStructure
            ORDER BY CurriculumID
        """)
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_curriculum_info(self, curriculum_id) -> Optional[Tuple]:
        """Get curriculum information by ID"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT CurriculumID, CurriculumName, FacultyName 
            FROM SubjectStructure 
            WHERE CurriculumID = ?
        """, (int(curriculum_id),))
        result = cursor.fetchone()
        cursor.close()
        return result

    def get_subjects_by_semester(self, semester) -> List[Tuple]:
        """Get all subjects offered in specific semester across all curriculums"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT CurriculumID, CurriculumName, FacultyName, SubjectID, Semester 
            FROM SubjectStructure 
            WHERE Semester = ?
            ORDER BY CurriculumID, SubjectID
        """, (int(semester),))
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_curriculum_subjects_count(self, curriculum_id) -> Tuple[int, int]:
        """Get count of subjects per semester for specific curriculum"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT Semester, COUNT(*) 
            FROM SubjectStructure 
            WHERE CurriculumID = ?
            GROUP BY Semester
        """, (int(curriculum_id),))
        result = cursor.fetchall()
        cursor.close()
        
        semester_counts = {1: 0, 2: 0}
        for semester, count in result:
            semester_counts[semester] = count
        
        return (semester_counts[1], semester_counts[2])

    def get_all_required_subjects_for_student(self, curriculum_id) -> List[Tuple]:
        """Get all required subject IDs and their semesters for a curriculum"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT SubjectID, Semester 
            FROM SubjectStructure 
            WHERE CurriculumID = ?
            ORDER BY Semester, SubjectID
        """, (int(curriculum_id),))
        result = cursor.fetchall()
        cursor.close()
        return result

    def is_subject_required_in_curriculum(self, curriculum_id, subject_id) -> bool:
        """Check if a subject is required in specific curriculum"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM SubjectStructure 
            WHERE CurriculumID = ? AND SubjectID = ?
        """, (int(curriculum_id), str(subject_id)))  # เปลี่ยนเป็น str เพราะ SubjectID เป็น TEXT
        result = cursor.fetchone()
        cursor.close()
        return result[0] > 0

    def get_subject_semester_in_curriculum(self, curriculum_id, subject_id) -> Optional[int]:
        """Get the semester when subject is offered in specific curriculum"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT Semester 
            FROM SubjectStructure 
            WHERE CurriculumID = ? AND SubjectID = ?
        """, (int(curriculum_id), str(subject_id)))  # เปลี่ยนเป็น str เพราะ SubjectID เป็น TEXT
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None

    def get_curriculums_by_faculty(self, faculty_name: str) -> List[Tuple]:
        """Get curriculums by faculty name"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT CurriculumID, CurriculumName, FacultyName 
            FROM SubjectStructure 
            WHERE FacultyName LIKE ?
            ORDER BY CurriculumID
        """, (f"%{faculty_name}%",))
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_curriculum_statistics(self) -> List[Tuple]:
        """Get curriculum statistics"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT CurriculumID, CurriculumName, FacultyName,
                   COUNT(*) as TotalSubjects,
                   SUM(CASE WHEN Semester = 1 THEN 1 ELSE 0 END) as Semester1Count,
                   SUM(CASE WHEN Semester = 2 THEN 1 ELSE 0 END) as Semester2Count
            FROM SubjectStructure
            GROUP BY CurriculumID, CurriculumName, FacultyName
            ORDER BY CurriculumID
        """)
        result = cursor.fetchall()
        cursor.close()
        return result

    def close_connection(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()