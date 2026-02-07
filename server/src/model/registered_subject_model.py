import sqlite3
from typing import List, Tuple, Optional

class RegisteredSubjectModel:
    """
    SQLite-backed model for RegisteredSubject table.
    """

    # Valid grades mapping
    GRADES = {
        "A": 4.0, "B+": 3.5, "B": 3.0, "C+": 2.5, 
        "C": 2.0, "D+": 1.5, "D": 1.0, "F": 0.0
    }

    PASSING_GRADES = {"A", "B+", "B", "C+", "C", "D+", "D"}
    FAILING_GRADES = {"F"}

    def __init__(self, db_path: str = "src/database/school_registration.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

    def get_all_registered_subjects(self) -> List[Tuple]:
        """Get all registered subjects data"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT StudentID, SubjectID, Grade 
            FROM RegisteredSubject
            ORDER BY StudentID, SubjectID
        """)
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_student_registered_subjects(self, student_id) -> List[Tuple]:
        """Get all subjects registered by specific student"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT rs.StudentID, rs.SubjectID, rs.Grade, s.SubjectName, s.Credits
            FROM RegisteredSubject rs
            LEFT JOIN Subjects s ON rs.SubjectID = s.SubjectID
            WHERE rs.StudentID = ?
            ORDER BY rs.SubjectID
        """, (int(student_id),))
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_subject_registered_students(self, subject_id) -> List[Tuple]:
        """Get all students registered for specific subject"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT rs.StudentID, rs.SubjectID, rs.Grade, 
                   st.FirstName, st.LastName, st.Title
            FROM RegisteredSubject rs
            LEFT JOIN Students st ON rs.StudentID = st.StudentID
            WHERE rs.SubjectID = ?
            ORDER BY st.FirstName, st.LastName
        """, (str(subject_id),))
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_student_subject_grade(self, student_id, subject_id) -> Optional[str]:
        """Get grade for specific student-subject combination"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT Grade 
            FROM RegisteredSubject 
            WHERE StudentID = ? AND SubjectID = ?
        """, (int(student_id), str(subject_id)))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None

    def is_student_registered_for_subject(self, student_id, subject_id) -> bool:
        """Check if student is registered for specific subject"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM RegisteredSubject 
            WHERE StudentID = ? AND SubjectID = ?
        """, (int(student_id), str(subject_id)))
        result = cursor.fetchone()
        cursor.close()
        return result[0] > 0

    def has_student_passed_subject(self, student_id, subject_id) -> bool:
        """Check if student has passed specific subject"""
        grade = self.get_student_subject_grade(student_id, subject_id)
        return grade is not None and grade in self.PASSING_GRADES

    def get_student_passed_subjects(self, student_id) -> List[str]:
        """Get list of subject IDs that student has passed"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT SubjectID 
            FROM RegisteredSubject 
            WHERE StudentID = ? AND Grade IN ('A', 'B+', 'B', 'C+', 'C', 'D+', 'D')
        """, (int(student_id),))
        result = cursor.fetchall()
        cursor.close()
        return [row[0] for row in result]

    def get_student_failed_subjects(self, student_id) -> List[str]:
        """Get list of subject IDs that student has failed"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT SubjectID 
            FROM RegisteredSubject 
            WHERE StudentID = ? AND Grade = 'F'
        """, (int(student_id),))
        result = cursor.fetchall()
        cursor.close()
        return [row[0] for row in result]

    def get_subject_enrollment_count(self, subject_id) -> int:
        """Get number of students enrolled in specific subject"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM RegisteredSubject 
            WHERE SubjectID = ?
        """, (str(subject_id),))
        result = cursor.fetchone()
        cursor.close()
        return result[0]

    def get_subject_grade_statistics(self, subject_id) -> dict:
        """Get grade distribution statistics for specific subject"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT Grade, COUNT(*) 
            FROM RegisteredSubject 
            WHERE SubjectID = ? AND Grade IS NOT NULL AND Grade != ''
            GROUP BY Grade
        """, (str(subject_id),))
        result = cursor.fetchall()
        cursor.close()
        
        total_students = sum(count for _, count in result)
        if total_students == 0:
            return {
                "total_students": 0,
                "grade_distribution": {},
                "pass_rate": 0.0,
                "average_gpa": 0.0
            }
        
        grade_count = {grade: count for grade, count in result}
        passed_count = sum(count for grade, count in result if grade in self.PASSING_GRADES)
        total_gpa = sum(self.GRADES[grade] * count for grade, count in result if grade in self.GRADES)
        
        return {
            "total_students": total_students,
            "grade_distribution": grade_count,
            "pass_rate": (passed_count / total_students) * 100,
            "average_gpa": total_gpa / total_students
        }

    def get_student_gpa(self, student_id) -> float:
        """Calculate student's GPA from all registered subjects"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT Grade 
            FROM RegisteredSubject 
            WHERE StudentID = ? AND Grade IS NOT NULL AND Grade != ''
        """, (int(student_id),))
        result = cursor.fetchall()
        cursor.close()
        
        if not result:
            return 0.0
        
        grades = [row[0] for row in result]
        total_points = sum(self.GRADES[grade] for grade in grades if grade in self.GRADES)
        return total_points / len(grades)

    def can_register_for_subject(self, student_id, subject_id, subjects_model) -> Tuple[bool, str]:
        """Check if student can register for subject (considering prerequisites)"""
        # Check if already registered
        if self.is_student_registered_for_subject(student_id, subject_id):
            return False, "Already registered for this subject"
        
        # Get subject info to check prerequisites
        subject_info = subjects_model.get_subject_by_id(subject_id)
        if not subject_info:
            return False, "Subject not found"
        
        prerequisite_id = subject_info[4]  # PrerequisiteSubjectID is at index 4
        
        # If no prerequisite, can register
        if prerequisite_id is None:
            return True, "No prerequisites required"
        
        # Check if student has passed the prerequisite
        if self.has_student_passed_subject(student_id, prerequisite_id):
            return True, "Prerequisites satisfied"
        else:
            return False, f"Must pass prerequisite subject ID: {prerequisite_id}"

    def register_student_for_subject(self, student_id, subject_id, grade: str = "") -> bool:
        """Register student for subject (initially without grade)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO RegisteredSubject (StudentID, SubjectID, Grade)
                VALUES (?, ?, ?)
            """, (int(student_id), str(subject_id), grade))
            self.conn.commit()
            cursor.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def update_student_grade(self, student_id, subject_id, grade: str) -> bool:
        """Update grade for student-subject combination"""
        if grade.upper() not in self.GRADES:
            return False
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE RegisteredSubject 
                SET Grade = ? 
                WHERE StudentID = ? AND SubjectID = ?
            """, (grade.upper(), int(student_id), str(subject_id)))
            self.conn.commit()
            cursor.close()
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def get_students_without_grades_for_subject(self, subject_id) -> List[int]:
        """Get student IDs who are registered for subject but don't have grades yet"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT StudentID 
            FROM RegisteredSubject 
            WHERE SubjectID = ? AND (Grade IS NULL OR Grade = '')
        """, (str(subject_id),))
        result = cursor.fetchall()
        cursor.close()
        return [row[0] for row in result]

    def get_subject_grading_summary(self, subject_id) -> dict:
        """Get grading summary for admin view"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT rs.StudentID, rs.SubjectID, rs.Grade, 
                   st.FirstName, st.LastName, st.Title
            FROM RegisteredSubject rs
            LEFT JOIN Students st ON rs.StudentID = st.StudentID
            WHERE rs.SubjectID = ?
            ORDER BY st.FirstName, st.LastName
        """, (str(subject_id),))
        all_students = cursor.fetchall()
        cursor.close()
        
        graded_students = [s for s in all_students if s[2] and s[2] != ""]
        ungraded_students = [s for s in all_students if not s[2] or s[2] == ""]
        
        return {
            "total_registered": len(all_students),
            "graded_count": len(graded_students),
            "ungraded_count": len(ungraded_students),
            "graded_students": graded_students,
            "ungraded_students": [(s[0], s[1], s[3], s[4], s[5]) for s in ungraded_students]
        }

    def remove_student_registration(self, student_id, subject_id) -> bool:
        """Remove student registration for subject"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                DELETE FROM RegisteredSubject 
                WHERE StudentID = ? AND SubjectID = ?
            """, (int(student_id), str(subject_id)))
            self.conn.commit()
            cursor.close()
            return cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def close_connection(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()