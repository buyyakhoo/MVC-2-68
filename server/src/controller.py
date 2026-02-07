from flask import Flask, jsonify, request, session
from flask_cors import CORS
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model.students_model import StudentsModel
from model.subjects_model import SubjectsModel
from model.subject_structure_model import SubjectStructureModel
from model.registered_subject_model import RegisteredSubjectModel

app = Flask(__name__)
CORS(app)
app.secret_key = 'school_registration_secret_key'  # For session management

# ✅ อนุญาต origin ของ Live Server และส่งคุกกี้ได้
CORS(app,
     supports_credentials=True,
     resources={r"/*": {"origins": ["http://127.0.0.1:5500","http://localhost:5500"],
                        "allow_headers": ["Content-Type","X-User-ID","X-User-Type"]}})

# ✅ ตั้งค่า cookie ของ session ให้ข้ามไซต์ได้ขณะ dev
# หมายเหตุ: ปกติ SameSite=None ต้องคู่กับ Secure=True
# แต่บน localhost ส่วนใหญ่เบราว์เซอร์ผ่อนปรน; ถ้าบราว์เซอร์คุณยังบล็อค ให้ใช้ https หรือเสิร์ฟไฟล์ผ่าน Flask ให้เป็น same-origin
app.config.update(
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_SECURE=False  # ถ้าใช้ https ค่อยเปลี่ยนเป็น True
)

def _resolve_user_from_session_or_headers():
    uid = session.get("user_id")
    utype = session.get("user_type")
    if uid is not None and utype:
        return int(uid), utype
    # fallback จาก localStorage ที่ฝั่ง client ส่งมา
    hdr_uid = request.headers.get("X-User-ID")
    hdr_utype = request.headers.get("X-User-Type")
    if hdr_uid and hdr_utype:
        try:
            return int(hdr_uid), hdr_utype
        except ValueError:
            return None, None
    return None, None

def _require_admin():
    uid, utype = _resolve_user_from_session_or_headers()
    return uid is not None and utype == 'admin'


# ===============================
# AUTHENTICATION ENDPOINTS
# ===============================

@app.route("/")
def index():
    return jsonify({"message": "School Registration System API", "version": "1.0"})

@app.route("/login", methods=["POST"])
def login():
    """Simple authentication for students and admin"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    req_data = request.get_json()
    
    if 'user_id' not in req_data or 'user_type' not in req_data:
        return jsonify({"error": "user_id and user_type are required"}), 400
    
    user_id = req_data['user_id']
    user_type = req_data['user_type']  # 'student' or 'admin'
    
    if user_type == 'admin' and user_id == 99999999:
        session['user_id'] = user_id
        session['user_type'] = 'admin'
        return jsonify({"status": "success", "user_type": "admin", "user_id": user_id}), 200
    elif user_type == 'student':
        # Verify student exists
        sm = StudentsModel()
        student = sm.get_student_by_id(user_id)
        sm.close_connection()
        
        if student:
            session['user_id'] = user_id
            session['user_type'] = 'student'
            return jsonify({"status": "success", "user_type": "student", "user_id": user_id}), 200
        else:
            return jsonify({"error": "Student not found"}), 404
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route("/logout", methods=["POST"])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({"status": "success", "message": "Logged out"}), 200

# ===============================
# STUDENT MANAGEMENT ENDPOINTS (Admin only)
# ===============================

@app.route("/students", methods=["GET"])
def get_all_students():
    """หน้ารวมนักเรียน: แสดงรายชื่อนักเรียน (Admin only)"""
    if not _require_admin():
        return jsonify({"error": "Admin access required"}), 403
    
    sm = StudentsModel()
    
    # Query parameters for filtering and sorting
    school_filter = request.args.get('school', '')
    search_term = request.args.get('search', '')
    sort_by = request.args.get('sort', 'name')  # 'name' or 'age'
    
    try:
        if search_term:
            students = sm.search_students(search_term)
        elif school_filter:
            students = sm.get_students_by_school(school_filter)
        elif sort_by == 'age':
            students = sm.get_students_sorted_by_age()
        else:
            students = sm.get_students_sorted_by_name()
        
        # Add age to each student
        students_with_age = []
        for student in students:
            age = sm.get_student_age(student[0])
            student_data = {
                "StudentID": student[0],
                "Title": student[1],
                "FirstName": student[2],
                "LastName": student[3],
                "BirthDate": student[4],
                "CurrentSchool": student[5],
                "Email": student[6],
                "CurriculumID": student[7],
                "Age": age
            }
            students_with_age.append(student_data)
        
        # Get unique schools for filtering
        schools = sm.get_unique_schools()
        
        sm.close_connection()
        
        return jsonify({
            "students": students_with_age,
            "schools": schools,
            "total": len(students_with_age)
        }), 200
        
    except Exception as e:
        sm.close_connection()
        return jsonify({"error": str(e)}), 500

@app.route("/students/<int:student_id>", methods=["GET"])
def get_student_profile(student_id):
    """หน้าประวัติของนักเรียน: แสดงรายละเอียด และรายวิชาที่ลงและได้รับเกรดแล้ว"""
    # ✅ ใช้ตัวตนจาก session หรือ header (fallback)
    uid, utype = _resolve_user_from_session_or_headers()
    if not uid or utype not in ('student', 'admin'):
        return jsonify({"error": "Authentication required"}), 401
    if utype == 'student' and uid != student_id:
        return jsonify({"error": "Access denied"}), 403

    sm = StudentsModel()
    rs = RegisteredSubjectModel()
    try:
        student = sm.get_student_by_id(student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404

        age = sm.get_student_age(student_id)
        eligible = sm.is_student_eligible(student_id)
        registered_subjects = rs.get_student_registered_subjects(student_id)
        gpa = rs.get_student_gpa(student_id)

        student_data = {
            "StudentID": student[0],
            "Title": student[1],
            "FirstName": student[2],
            "LastName": student[3],
            "BirthDate": student[4],
            "CurrentSchool": student[5],
            "Email": student[6],
            "CurriculumID": student[7],
            "Age": age,
            "Eligible": eligible,
            "GPA": round(gpa, 2),
            "RegisteredSubjects": [
                {
                    "SubjectID": subj[1],
                    "Grade": subj[2],
                    "SubjectName": subj[3],
                    "Credits": subj[4]
                } for subj in registered_subjects
            ]
        }
        return jsonify(student_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        sm.close_connection()
        rs.close_connection()


# ===============================
# SUBJECT REGISTRATION ENDPOINTS
# ===============================

@app.route("/students/<int:student_id>/available_subjects", methods=["GET"])
def get_available_subjects_for_registration(student_id):
    """หน้าลงทะเบียนเรียน: แสดงรายละเอียดรายวิชาในหลักสูตรที่ยังไม่ได้ลงทะเบียน"""
    # Students can only view their own available subjects
    if session.get('user_type') == 'student' and session.get('user_id') != student_id:
        return jsonify({"error": "Access denied"}), 403
    elif session.get('user_type') not in ['student', 'admin']:
        return jsonify({"error": "Authentication required"}), 401
    
    sm = StudentsModel()
    ss = SubjectStructureModel()
    rs = RegisteredSubjectModel()
    subj = SubjectsModel()
    
    try:
        # Get student info
        student = sm.get_student_by_id(student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        # Check if student is eligible (age >= 15)
        if not sm.is_student_eligible(student_id):
            return jsonify({"error": "Student is not eligible (age must be >= 15)"}), 400
        
        curriculum_id = student[7]
        
        # Get all required subjects for this curriculum
        required_subjects = ss.get_all_required_subjects_for_student(curriculum_id)
        
        # Get already registered subjects
        registered_subjects = [reg[1] for reg in rs.get_student_registered_subjects(student_id)]
        
        # Filter unregistered subjects
        available_subjects = []
        for subj_id, semester in required_subjects:
            if subj_id not in registered_subjects:
                subject_info = subj.get_subject_by_id(subj_id)
                if subject_info:
                    # Check if can register (prerequisites)
                    can_register, reason = rs.can_register_for_subject(student_id, subj_id, subj)
                    
                    subject_data = {
                        "SubjectID": subject_info[0],
                        "SubjectName": subject_info[1],
                        "Credits": subject_info[2],
                        "Instructor": subject_info[3],
                        "PrerequisiteSubjectID": subject_info[4],
                        "Semester": semester,
                        "CanRegister": can_register,
                        "Reason": reason
                    }
                    available_subjects.append(subject_data)
        
        sm.close_connection()
        ss.close_connection()
        rs.close_connection()
        subj.close_connection()
        
        return jsonify({
            "student_id": student_id,
            "curriculum_id": curriculum_id,
            "available_subjects": available_subjects,
            "total": len(available_subjects)
        }), 200
        
    except Exception as e:
        sm.close_connection()
        ss.close_connection()
        rs.close_connection()
        subj.close_connection()
        return jsonify({"error": str(e)}), 500

@app.route("/register_subject", methods=["POST"])
def register_subject():
    """ลงทะเบียนเรียน"""
    if session.get('user_type') not in ['student', 'admin']:
        return jsonify({"error": "Authentication required"}), 401
    
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    req_data = request.get_json()
    
    if 'student_id' not in req_data or 'subject_id' not in req_data:
        return jsonify({"error": "student_id and subject_id are required"}), 400
    
    student_id = req_data['student_id']
    subject_id = req_data['subject_id']
    
    # Students can only register for themselves
    if session.get('user_type') == 'student' and session.get('user_id') != student_id:
        return jsonify({"error": "Access denied"}), 403
    
    sm = StudentsModel()
    rs = RegisteredSubjectModel()
    subj = SubjectsModel()
    
    try:
        # Check if student exists and is eligible
        student = sm.get_student_by_id(student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        if not sm.is_student_eligible(student_id):
            return jsonify({"error": "Student is not eligible (age must be >= 15)"}), 400
        
        # Check if can register
        can_register, reason = rs.can_register_for_subject(student_id, subject_id, subj)
        
        if not can_register:
            return jsonify({"error": reason}), 400
        
        # Register student
        success = rs.register_student_for_subject(student_id, subject_id)
        
        if success:
            return jsonify({"status": "success", "message": "Registration successful"}), 200
        else:
            return jsonify({"error": "Registration failed"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        sm.close_connection()
        rs.close_connection()
        subj.close_connection()

# ===============================
# GRADING ENDPOINTS (Admin only)
# ===============================

@app.route("/subjects/<subject_id>/students", methods=["GET"])
def get_subject_students_for_grading(subject_id):
    """หน้ากรอกเกรดสำหรับรายวิชา: แสดงรายชื่อนักเรียนที่ลงทะเบียน (Admin only)"""
    if not _require_admin():
        return jsonify({"error": "Admin access required"}), 403
    
    rs = RegisteredSubjectModel()
    subj = SubjectsModel()
    
    try:
        # Get subject info
        subject_info = subj.get_subject_by_id(subject_id)
        if not subject_info:
            return jsonify({"error": "Subject not found"}), 404
        
        # Get registered students
        registered_students = rs.get_subject_registered_students(subject_id)
        
        # Get grading summary
        grading_summary = rs.get_subject_grading_summary(subject_id)
        
        students_data = [
            {
                "StudentID": student[0],
                "SubjectID": student[1],
                "Grade": student[2],
                "FirstName": student[3],
                "LastName": student[4],
                "Title": student[5]
            } for student in registered_students
        ]
        
        subject_data = {
            "SubjectID": subject_info[0],
            "SubjectName": subject_info[1],
            "Credits": subject_info[2],
            "Instructor": subject_info[3],
            "TotalRegistered": grading_summary['total_registered'],
            "GradedCount": grading_summary['graded_count'],
            "UngradedCount": grading_summary['ungraded_count'],
            "Students": students_data
        }
        
        rs.close_connection()
        subj.close_connection()
        
        return jsonify(subject_data), 200
        
    except Exception as e:
        rs.close_connection()
        subj.close_connection()
        return jsonify({"error": str(e)}), 500

@app.route("/update_grade", methods=["POST"])
def update_grade():
    """อัพเดทเกรดของนักเรียน (Admin only)"""
    # เดิม: if session.get('user_type') != 'admin':
    if not _require_admin():                                  # ✅ ใช้ helper ที่อ่านจาก session หรือ header
        return jsonify({"error": "Admin access required"}), 403

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    req_data = request.get_json()
    required_fields = ['student_id', 'subject_id', 'grade']
    for field in required_fields:
        if field not in req_data:
            return jsonify({"error": f"{field} is required"}), 400

    student_id = int(req_data['student_id'])
    subject_id = req_data['subject_id']
    grade = (req_data['grade'] or "").upper()

    rs = RegisteredSubjectModel()
    try:
        # ถ้าอยาก "ล้างเกรด" อนุญาตให้ส่งค่าว่างได้ (คงไว้/เอาออกตามที่ต้องการ)
        if grade and grade not in rs.GRADES:
            return jsonify({"error": f"Invalid grade. Valid grades: {list(rs.GRADES.keys())}"}), 400

        success = rs.update_student_grade(student_id, subject_id, grade if grade else None)
        if success:
            return jsonify({"status": "success", "message": "Grade updated successfully"}), 200
        return jsonify({"error": "Grade update failed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        rs.close_connection()


# ===============================
# REPORTING ENDPOINTS
# ===============================

@app.route("/reports/curriculums", methods=["GET"])
def get_curriculum_report():
    """รายงานหลักสูตร"""
    if session.get('user_type') != 'admin':
        return jsonify({"error": "Admin access required"}), 403
    
    ss = SubjectStructureModel()
    
    try:
        curriculum_stats = ss.get_curriculum_statistics()
        
        report_data = [
            {
                "CurriculumID": stat[0],
                "CurriculumName": stat[1],
                "FacultyName": stat[2],
                "TotalSubjects": stat[3],
                "Semester1Count": stat[4],
                "Semester2Count": stat[5]
            } for stat in curriculum_stats
        ]
        
        ss.close_connection()
        
        return jsonify({
            "curriculums": report_data,
            "total_curriculums": len(report_data)
        }), 200
        
    except Exception as e:
        ss.close_connection()
        return jsonify({"error": str(e)}), 500

@app.route("/reports/subjects/<subject_id>/statistics", methods=["GET"])
def get_subject_statistics(subject_id):
    """รายงานสถิติของรายวิชา"""
    if session.get('user_type') != 'admin':
        return jsonify({"error": "Admin access required"}), 403
    
    rs = RegisteredSubjectModel()
    subj = SubjectsModel()
    
    try:
        # Get subject info
        subject_info = subj.get_subject_by_id(subject_id)
        if not subject_info:
            return jsonify({"error": "Subject not found"}), 404
        
        # Get statistics
        stats = rs.get_subject_grade_statistics(subject_id)
        enrollment_count = rs.get_subject_enrollment_count(subject_id)
        
        report_data = {
            "SubjectID": subject_info[0],
            "SubjectName": subject_info[1],
            "Credits": subject_info[2],
            "Instructor": subject_info[3],
            "EnrollmentCount": enrollment_count,
            "Statistics": stats
        }
        
        rs.close_connection()
        subj.close_connection()
        
        return jsonify(report_data), 200
        
    except Exception as e:
        rs.close_connection()
        subj.close_connection()
        return jsonify({"error": str(e)}), 500
    
# --- /me/profile ---
@app.route('/me/profile', methods=['GET'])
def me_profile():
    student_id, user_type = _resolve_user_from_session_or_headers()
    if not student_id or user_type != 'student':
        return jsonify({'error': 'Unauthorized'}), 401

    sm = StudentsModel()
    rs = RegisteredSubjectModel()
    try:
        student = sm.get_student_by_id(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404

        age = sm.get_student_age(student_id)
        eligible = sm.is_student_eligible(student_id)
        registered_subjects = rs.get_student_registered_subjects(student_id)
        gpa = rs.get_student_gpa(student_id)

        data = {
            "StudentID": student[0],
            "Title": student[1],
            "FirstName": student[2],
            "LastName": student[3],
            "BirthDate": student[4],
            "CurrentSchool": student[5],
            "Email": student[6],
            "CurriculumID": student[7],
            "Age": age,
            "Eligible": eligible,
            "GPA": round(gpa, 2),
            "RegisteredSubjects": [
                {
                    "SubjectID": r[1],
                    "Grade": r[2],
                    "SubjectName": r[3],
                    "Credits": r[4]
                } for r in registered_subjects
            ]
        }
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        sm.close_connection()
        rs.close_connection()

# --- /me/registered-subjects ---
@app.route('/me/registered-subjects', methods=['GET'])
def me_registered_subjects():
    student_id, user_type = _resolve_user_from_session_or_headers()
    if not student_id or user_type != 'student':
        return jsonify({'error': 'Unauthorized'}), 401

    rs = RegisteredSubjectModel()
    try:
        regs = rs.get_student_registered_subjects(student_id)
        return jsonify([
            {
                "StudentID": r[0],
                "SubjectID": r[1],
                "Grade": r[2],
                "SubjectName": r[3],
                "Credits": r[4]
            } for r in regs
        ]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        rs.close_connection()

# --- /me/unregistered-subjects (ใหม่) ---
@app.route('/me/unregistered-subjects', methods=['GET'])
def me_unregistered_subjects():
    student_id, user_type = _resolve_user_from_session_or_headers()
    if not student_id or user_type != 'student':
        return jsonify({'error': 'Unauthorized'}), 401

    sm = StudentsModel()
    ss = SubjectStructureModel()
    rs = RegisteredSubjectModel()
    subj = SubjectsModel()
    try:
        student = sm.get_student_by_id(student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404

        curriculum_id = student[7]
        required = ss.get_all_required_subjects_for_student(curriculum_id)  # [(SubjectID, Semester)]
        registered_ids = [r[1] for r in rs.get_student_registered_subjects(student_id)]

        unregistered = []
        for sid, sem in required:
            if sid not in registered_ids:
                info = subj.get_subject_by_id(sid)
                if info:
                    unregistered.append({
                        "SubjectID": info[0],
                        "SubjectName": info[1],
                        "Credits": info[2],
                        "Instructor": info[3],
                        "PrerequisiteSubjectID": info[4],
                        "Semester": sem
                    })
        return jsonify(unregistered), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        sm.close_connection(); ss.close_connection(); rs.close_connection(); subj.close_connection()


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)