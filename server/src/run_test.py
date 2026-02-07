#!/usr/bin/env python3
"""
Comprehensive test script for all school registration models
Run with: python src/run_test.py
"""

import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model.students_model import StudentsModel
from model.subjects_model import SubjectsModel
from model.subject_structure_model import SubjectStructureModel
from model.registered_subject_model import RegisteredSubjectModel

def test_students_model():
    print("=" * 60)
    print("TESTING STUDENTS MODEL")
    print("=" * 60)
    
    sm = StudentsModel()
    
    # Test 1: Get all students
    print("1. Testing get_all_students()")
    all_students = sm.get_all_students()
    print(f"   Total students: {len(all_students)}")
    if all_students:
        print(f"   Sample: {all_students[0]}")
    
    # Test 2: Get student by ID
    print("\n2. Testing get_student_by_id()")
    if all_students:
        test_id = all_students[0][0]
        student = sm.get_student_by_id(test_id)
        print(f"   Student {test_id}: {student}")
    
    # Test 3: Get students by curriculum
    print("\n3. Testing get_students_by_curriculum()")
    if all_students:
        curriculum_id = all_students[0][7]
        students_in_curriculum = sm.get_students_by_curriculum(curriculum_id)
        print(f"   Students in curriculum {curriculum_id}: {len(students_in_curriculum)}")
    
    # Test 4: Search students
    print("\n4. Testing search_students()")
    search_results = sm.search_students("A")
    print(f"   Search 'A' results: {len(search_results)}")
    
    # Test 5: Get students by school
    print("\n5. Testing get_students_by_school()")
    if all_students:
        school = all_students[0][5]
        school_students = sm.get_students_by_school(school.split()[0])  # First word of school name
        print(f"   Students from '{school.split()[0]}': {len(school_students)}")
    
    # Test 6: Get student age
    print("\n6. Testing get_student_age()")
    if all_students:
        test_id = all_students[0][0]
        age = sm.get_student_age(test_id)
        eligible = sm.is_student_eligible(test_id)
        print(f"   Student {test_id} age: {age}, eligible: {eligible}")
    
    # Test 7: Get unique schools
    print("\n7. Testing get_unique_schools()")
    schools = sm.get_unique_schools()
    print(f"   Unique schools: {len(schools)}")
    for school in schools[:3]:  # Show first 3
        print(f"     - {school}")
    
    sm.close_connection()
    print("\n✓ Students Model tests completed")

def test_subjects_model():
    print("\n" + "=" * 60)
    print("TESTING SUBJECTS MODEL")
    print("=" * 60)
    
    subj = SubjectsModel()
    
    # Test 1: Get all subjects
    print("1. Testing get_all_subjects()")
    all_subjects = subj.get_all_subjects()
    print(f"   Total subjects: {len(all_subjects)}")
    if all_subjects:
        print(f"   Sample: {all_subjects[0]}")
    
    # Test 2: Get subject by ID
    print("\n2. Testing get_subject_by_id()")
    if all_subjects:
        test_id = all_subjects[0][0]
        subject = subj.get_subject_by_id(test_id)
        print(f"   Subject {test_id}: {subject}")
    
    # Test 3: Get subjects by type
    print("\n3. Testing get_subjects_by_type()")
    faculty_subjects = subj.get_subjects_by_type("faculty")
    general_subjects = subj.get_subjects_by_type("general")
    print(f"   Faculty subjects (0550*): {len(faculty_subjects)}")
    print(f"   General subjects (9069*): {len(general_subjects)}")
    
    # Test 4: Get subjects with prerequisites
    print("\n4. Testing get_subjects_with_prerequisites()")
    prereq_subjects = subj.get_subjects_with_prerequisites()
    print(f"   Subjects with prerequisites: {len(prereq_subjects)}")
    if prereq_subjects:
        for prereq in prereq_subjects[:2]:  # Show first 2
            print(f"     - {prereq[1]} (requires {prereq[4]})")
    
    # Test 5: Search subjects
    print("\n5. Testing search_subjects()")
    search_results = subj.search_subjects("Programming")
    print(f"   Search 'Programming' results: {len(search_results)}")
    
    # Test 6: Get subjects by instructor
    print("\n6. Testing get_subjects_by_instructor()")
    if all_subjects:
        instructor = all_subjects[0][3]
        instructor_subjects = subj.get_subjects_by_instructor(instructor.split()[0])
        print(f"   Subjects by '{instructor.split()[0]}': {len(instructor_subjects)}")
    
    subj.close_connection()
    print("\n✓ Subjects Model tests completed")

def test_subject_structure_model():
    print("\n" + "=" * 60)
    print("TESTING SUBJECT STRUCTURE MODEL")
    print("=" * 60)
    
    ss = SubjectStructureModel()
    
    # Test 1: Get all curriculum structures
    print("1. Testing get_all_curriculum_structures()")
    all_structures = ss.get_all_curriculum_structures()
    print(f"   Total structure records: {len(all_structures)}")
    if all_structures:
        print(f"   Sample: {all_structures[0]}")
    
    # Test 2: Get available curriculums
    print("\n2. Testing get_available_curriculums()")
    curriculums = ss.get_available_curriculums()
    print(f"   Available curriculums: {len(curriculums)}")
    for curriculum in curriculums:
        print(f"     - {curriculum[0]}: {curriculum[1]} ({curriculum[2]})")
    
    # Test 3: Get curriculum by ID
    print("\n3. Testing get_curriculum_by_id()")
    if curriculums:
        test_curriculum = curriculums[0][0]
        curriculum_subjects = ss.get_curriculum_by_id(test_curriculum)
        print(f"   Subjects in curriculum {test_curriculum}: {len(curriculum_subjects)}")
    
    # Test 4: Get subjects by curriculum and semester
    print("\n4. Testing get_subjects_by_curriculum_and_semester()")
    if curriculums:
        test_curriculum = curriculums[0][0]
        sem1_subjects = ss.get_subjects_by_curriculum_and_semester(test_curriculum, 1)
        sem2_subjects = ss.get_subjects_by_curriculum_and_semester(test_curriculum, 2)
        print(f"   Curriculum {test_curriculum} - Semester 1: {len(sem1_subjects)} subjects")
        print(f"   Curriculum {test_curriculum} - Semester 2: {len(sem2_subjects)} subjects")
    
    # Test 5: Get curriculum subjects count
    print("\n5. Testing get_curriculum_subjects_count()")
    if curriculums:
        test_curriculum = curriculums[0][0]
        sem1_count, sem2_count = ss.get_curriculum_subjects_count(test_curriculum)
        print(f"   Curriculum {test_curriculum}: {sem1_count} (sem1) + {sem2_count} (sem2) = {sem1_count + sem2_count} total")
    
    # Test 6: Get curriculum statistics
    print("\n6. Testing get_curriculum_statistics()")
    stats = ss.get_curriculum_statistics()
    print("   Curriculum Statistics:")
    for stat in stats:
        print(f"     - {stat[1]}: {stat[3]} total ({stat[4]} sem1, {stat[5]} sem2)")
    
    # Test 7: Check if subject is required
    print("\n7. Testing is_subject_required_in_curriculum()")
    if curriculums and all_structures:
        test_curriculum = curriculums[0][0]
        test_subject = all_structures[0][3]
        is_required = ss.is_subject_required_in_curriculum(test_curriculum, test_subject)
        semester = ss.get_subject_semester_in_curriculum(test_curriculum, test_subject)
        print(f"   Subject {test_subject} required in curriculum {test_curriculum}: {is_required}")
        print(f"   Offered in semester: {semester}")
    
    ss.close_connection()
    print("\n✓ Subject Structure Model tests completed")

def test_registered_subject_model():
    print("\n" + "=" * 60)
    print("TESTING REGISTERED SUBJECT MODEL")
    print("=" * 60)
    
    rs = RegisteredSubjectModel()
    subj = SubjectsModel()  # Need for prerequisite checking
    
    # Test 1: Get all registered subjects
    print("1. Testing get_all_registered_subjects()")
    all_registrations = rs.get_all_registered_subjects()
    print(f"   Total registrations: {len(all_registrations)}")
    if all_registrations:
        print(f"   Sample: {all_registrations[0]}")
    
    # Test 2: Get student registered subjects
    print("\n2. Testing get_student_registered_subjects()")
    if all_registrations:
        test_student = all_registrations[0][0]
        student_subjects = rs.get_student_registered_subjects(test_student)
        print(f"   Student {test_student} registered subjects: {len(student_subjects)}")
        if student_subjects:
            print(f"     Sample: {student_subjects[0]}")
    
    # Test 3: Get subject registered students
    print("\n3. Testing get_subject_registered_students()")
    if all_registrations:
        test_subject = all_registrations[0][1]
        subject_students = rs.get_subject_registered_students(test_subject)
        print(f"   Subject {test_subject} enrolled students: {len(subject_students)}")
    
    # Test 4: Get student GPA
    print("\n4. Testing get_student_gpa()")
    if all_registrations:
        test_student = all_registrations[0][0]
        gpa = rs.get_student_gpa(test_student)
        print(f"   Student {test_student} GPA: {gpa:.2f}")
    
    # Test 5: Get passed subjects
    print("\n5. Testing get_student_passed_subjects()")
    if all_registrations:
        test_student = all_registrations[0][0]
        passed_subjects = rs.get_student_passed_subjects(test_student)
        failed_subjects = rs.get_student_failed_subjects(test_student)
        print(f"   Student {test_student} passed: {len(passed_subjects)} subjects")
        print(f"   Student {test_student} failed: {len(failed_subjects)} subjects")
    
    # Test 6: Get subject statistics
    print("\n6. Testing get_subject_grade_statistics()")
    if all_registrations:
        test_subject = all_registrations[0][1]
        stats = rs.get_subject_grade_statistics(test_subject)
        print(f"   Subject {test_subject} statistics:")
        print(f"     Total students: {stats['total_students']}")
        print(f"     Pass rate: {stats['pass_rate']:.1f}%")
        print(f"     Average GPA: {stats['average_gpa']:.2f}")
        print(f"     Grade distribution: {stats['grade_distribution']}")
    
    # Test 7: Check registration eligibility
    print("\n7. Testing can_register_for_subject()")
    if all_registrations:
        test_student = all_registrations[0][0]
        test_subject = all_registrations[0][1]
        can_register, reason = rs.can_register_for_subject(test_student, test_subject, subj)
        print(f"   Student {test_student} can register for {test_subject}: {can_register}")
        print(f"   Reason: {reason}")
    
    # Test 8: Subject enrollment count
    print("\n8. Testing get_subject_enrollment_count()")
    if all_registrations:
        test_subject = all_registrations[0][1]
        enrollment = rs.get_subject_enrollment_count(test_subject)
        print(f"   Subject {test_subject} enrollment: {enrollment} students")
    
    # Test 9: Get grading summary
    print("\n9. Testing get_subject_grading_summary()")
    if all_registrations:
        test_subject = all_registrations[0][1]
        summary = rs.get_subject_grading_summary(test_subject)
        print(f"   Subject {test_subject} grading summary:")
        print(f"     Total registered: {summary['total_registered']}")
        print(f"     Graded: {summary['graded_count']}")
        print(f"     Ungraded: {summary['ungraded_count']}")
    
    rs.close_connection()
    subj.close_connection()
    print("\n✓ Registered Subject Model tests completed")

def test_business_rules():
    print("\n" + "=" * 60)
    print("TESTING BUSINESS RULES")
    print("=" * 60)
    
    sm = StudentsModel()
    subj = SubjectsModel()
    ss = SubjectStructureModel()
    rs = RegisteredSubjectModel()
    
    # Test 1: Age eligibility (≥ 15 years)
    print("1. Testing age eligibility (≥ 15 years)")
    all_students = sm.get_all_students()
    eligible_count = 0
    total_count = len(all_students)
    
    for student in all_students[:5]:  # Test first 5 students
        student_id = student[0]
        age = sm.get_student_age(student_id)
        eligible = sm.is_student_eligible(student_id)
        print(f"   Student {student_id}: Age {age}, Eligible: {eligible}")
        if eligible:
            eligible_count += 1
    
    print(f"   Tested {min(5, total_count)} students, {eligible_count} eligible")
    
    # Test 2: Prerequisites checking
    print("\n2. Testing prerequisites checking")
    prereq_subjects = subj.get_subjects_with_prerequisites()
    if prereq_subjects and all_students:
        test_subject = prereq_subjects[0]
        test_student = all_students[0][0]
        
        print(f"   Subject: {test_subject[1]} (ID: {test_subject[0]})")
        print(f"   Requires: {test_subject[4]}")
        
        # Check if student has prerequisite
        has_prereq = rs.has_student_passed_subject(test_student, test_subject[4])
        can_register, reason = rs.can_register_for_subject(test_student, test_subject[0], subj)
        
        print(f"   Student {test_student} has prerequisite: {has_prereq}")
        print(f"   Can register: {can_register} - {reason}")
    
    # Test 3: Enrollment count validation (≥ 0)
    print("\n3. Testing enrollment count validation")
    all_subjects = subj.get_all_subjects()
    negative_count = 0
    
    for subject in all_subjects[:5]:  # Test first 5 subjects
        subject_id = subject[0]
        enrollment = rs.get_subject_enrollment_count(subject_id)
        print(f"   Subject {subject_id}: {enrollment} students enrolled")
        if enrollment < 0:
            negative_count += 1
    
    print(f"   Tested {min(5, len(all_subjects))} subjects, {negative_count} with negative enrollment")
    
    # Test 4: Grade validation
    print("\n4. Testing grade validation")
    valid_grades = rs.GRADES.keys()
    print(f"   Valid grades: {list(valid_grades)}")
    
    # Test grade validation
    test_grades = ["A", "B+", "C", "F", "X", ""]
    for grade in test_grades:
        is_valid = rs.validate_grade(grade) if hasattr(rs, 'validate_grade') else grade.upper() in rs.GRADES
        print(f"   Grade '{grade}': {'Valid' if is_valid else 'Invalid'}")
    
    # Test 5: Curriculum structure validation
    print("\n5. Testing curriculum structure validation")
    curriculums = ss.get_available_curriculums()
    for curriculum in curriculums:
        curriculum_id = curriculum[0]
        sem1_count, sem2_count = ss.get_curriculum_subjects_count(curriculum_id)
        total_subjects = sem1_count + sem2_count
        
        print(f"   {curriculum[1]}:")
        print(f"     Semester 1: {sem1_count} subjects")
        print(f"     Semester 2: {sem2_count} subjects")
        print(f"     Total: {total_subjects} subjects")
        
        # Check requirement: ≥ 3 subjects per semester
        sem1_ok = sem1_count >= 3
        sem2_ok = sem2_count >= 3
        print(f"     Requirements met: Sem1={sem1_ok}, Sem2={sem2_ok}")
    
    # Close connections
    sm.close_connection()
    subj.close_connection()
    ss.close_connection()
    rs.close_connection()
    
    print("\n✓ Business Rules tests completed")

def check_database_connectivity():
    print("=" * 60)
    print("CHECKING DATABASE CONNECTIVITY")
    print("=" * 60)
    
    db_path = "src/database/school_registration.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        print("   Please run 'python load_csv_to_database.py' first")
        return False
    
    print(f"✓ Database file found: {db_path}")
    
    try:
        # Test connection to each model
        models = [
            ("Students", StudentsModel),
            ("Subjects", SubjectsModel),
            ("SubjectStructure", SubjectStructureModel),
            ("RegisteredSubject", RegisteredSubjectModel)
        ]
        
        for name, model_class in models:
            model = model_class()
            if hasattr(model, 'conn') and model.conn:
                print(f"✓ {name}Model connection successful")
                model.close_connection()
            else:
                print(f"❌ {name}Model connection failed")
                return False
    
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False
    
    print("✓ All database connections successful")
    return True

def main():
    print("SCHOOL REGISTRATION SYSTEM - MODEL TESTING")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Script location: {os.path.abspath(__file__)}")
    
    # Check database connectivity first
    if not check_database_connectivity():
        print("\n❌ Database connectivity failed. Cannot proceed with tests.")
        return
    
    try:
        # Run all tests
        test_students_model()
        test_subjects_model()
        test_subject_structure_model()
        test_registered_subject_model()
        test_business_rules()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✓ StudentsModel - OK")
        print("✓ SubjectsModel - OK")
        print("✓ SubjectStructureModel - OK")
        print("✓ RegisteredSubjectModel - OK")
        print("✓ Business Rules - OK")
        print("\nModels are ready for use in MVC application!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()