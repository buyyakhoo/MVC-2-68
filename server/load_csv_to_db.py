import sqlite3
import csv
import os

# สร้างโฟลเดอร์สำหรับ database
os.makedirs("src/database", exist_ok=True)

# เชื่อมต่อกับ SQLite database
db_path = "src/database/school_registration.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# เปิดใช้งาน foreign keys
cursor.execute("PRAGMA foreign_keys = ON")

def drop_all_tables():
    """ลบ tables ทั้งหมด"""
    cursor.execute("DROP TABLE IF EXISTS RegisteredSubject")
    cursor.execute("DROP TABLE IF EXISTS SubjectStructure")
    cursor.execute("DROP TABLE IF EXISTS Subjects")
    cursor.execute("DROP TABLE IF EXISTS Students")
    conn.commit()
    print("Dropped all existing tables")

def create_students_table():
    """สร้างตาราง Students"""
    cursor.execute('''
        CREATE TABLE Students (
            StudentID INTEGER PRIMARY KEY,
            Title TEXT NOT NULL,
            FirstName TEXT NOT NULL,
            LastName TEXT NOT NULL,
            BirthDate TEXT NOT NULL,
            CurrentSchool TEXT NOT NULL,
            Email TEXT NOT NULL,
            CurriculumID INTEGER NOT NULL
        )
    ''')
    print("Created Students table")

def create_subjects_table():
    """สร้างตาราง Subjects"""
    cursor.execute('''
        CREATE TABLE Subjects (
            SubjectID TEXT PRIMARY KEY,
            SubjectName TEXT NOT NULL,
            Credits INTEGER NOT NULL,
            Instructor TEXT NOT NULL,
            PrerequisiteSubjectID TEXT,
            FOREIGN KEY (PrerequisiteSubjectID) REFERENCES Subjects(SubjectID)
        )
    ''')
    print("Created Subjects table")

def create_subject_structure_table():
    """สร้างตาราง SubjectStructure"""
    cursor.execute('''
        CREATE TABLE SubjectStructure (
            CurriculumID INTEGER NOT NULL,
            CurriculumName TEXT NOT NULL,
            FacultyName TEXT NOT NULL,
            SubjectID TEXT NOT NULL,
            Semester INTEGER NOT NULL,
            PRIMARY KEY (CurriculumID, SubjectID),
            FOREIGN KEY (SubjectID) REFERENCES Subjects(SubjectID)
        )
    ''')
    print("Created SubjectStructure table")

def create_registered_subject_table():
    """สร้างตาราง RegisteredSubject"""
    cursor.execute('''
        CREATE TABLE RegisteredSubject (
            StudentID INTEGER NOT NULL,
            SubjectID TEXT NOT NULL,
            Grade TEXT,
            PRIMARY KEY (StudentID, SubjectID),
            FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
            FOREIGN KEY (SubjectID) REFERENCES Subjects(SubjectID)
        )
    ''')
    print("Created RegisteredSubject table")

def load_students_csv():
    """อ่านและ insert ข้อมูลจาก Students.csv"""
    with open('src/database/Students.csv', 'r', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        students_data = []
        
        for row in csv_reader:
            students_data.append((
                int(row['StudentID']),
                row['Title'].strip(),
                row['FirstName'].strip(),
                row['LastName'].strip(),
                row['BirthDate'].strip(),
                row['CurrentSchool'].strip(),
                row['Email'].strip(),
                int(row['CurriculumID'])
            ))
    
    cursor.executemany('''
        INSERT INTO Students (StudentID, Title, FirstName, LastName, BirthDate, CurrentSchool, Email, CurriculumID)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', students_data)
    
    print(f"Inserted {len(students_data)} records into Students table")

def load_subjects_csv():
    """อ่านและ insert ข้อมูลจาก Subjects.csv"""
    with open('src/database/Subjects.csv', 'r', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        subjects_data = []
        
        # Debug: แสดง column names ที่อ่านได้
        print(f"CSV columns found: {csv_reader.fieldnames}")
        
        for row in csv_reader:
            # Debug: แสดงข้อมูลแถวแรก
            if len(subjects_data) == 0:
                print(f"First row data: {dict(row)}")
            
            # ทำความสะอาด column names และ values
            clean_row = {}
            for key, value in row.items():
                clean_key = key.strip() if key else key
                clean_value = value.strip() if value else value
                clean_row[clean_key] = clean_value
            
            # หา column names ที่ถูกต้อง (อาจมีช่องว่างหรือตัวอักษรแปลก)
            subject_id_key = None
            subject_name_key = None
            credit_key = None
            professor_key = None
            prerequisite_key = None
            
            for key in clean_row.keys():
                key_lower = key.lower().strip()
                if 'subjectid' in key_lower:
                    subject_id_key = key
                elif 'subjectname' in key_lower:
                    subject_name_key = key
                elif 'credit' in key_lower:
                    credit_key = key
                elif 'professor' in key_lower:
                    professor_key = key
                elif 'prerequisite' in key_lower:
                    prerequisite_key = key
            
            # จัดการ PrerequisiteCode ที่อาจเป็นค่าว่าง (เก็บเป็น TEXT)
            prerequisite_id = None
            if prerequisite_key and clean_row[prerequisite_key]:
                prerequisite_id = clean_row[prerequisite_key].strip()
            
            subjects_data.append((
                clean_row[subject_id_key].strip(),  # เก็บเป็น TEXT เพื่อรักษาเลข 0 ข้างหน้า
                clean_row[subject_name_key],
                int(clean_row[credit_key]),
                clean_row[professor_key],
                prerequisite_id
            ))
    
    cursor.executemany('''
        INSERT INTO Subjects (SubjectID, SubjectName, Credits, Instructor, PrerequisiteSubjectID)
        VALUES (?, ?, ?, ?, ?)
    ''', subjects_data)
    
    print(f"Inserted {len(subjects_data)} records into Subjects table")

def load_subject_structure_csv():
    """อ่านและ insert ข้อมูลจาก SubjectStructure.csv"""
    with open('src/database/SubjectStructure.csv', 'r', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        structure_data = []
        
        for row in csv_reader:
            structure_data.append((
                int(row['CurriculumID']),
                row['CurriculumName'].strip(),
                row['FacultyName'].strip(),
                row['SubjectID'].strip(),  # เก็บเป็น TEXT เพื่อรักษาเลข 0 ข้างหน้า
                int(row['Semester'])
            ))
    
    cursor.executemany('''
        INSERT INTO SubjectStructure (CurriculumID, CurriculumName, FacultyName, SubjectID, Semester)
        VALUES (?, ?, ?, ?, ?)
    ''', structure_data)
    
    print(f"Inserted {len(structure_data)} records into SubjectStructure table")

def load_registered_subject_csv():
    """อ่านและ insert ข้อมูลจาก RegisteredSubject.csv"""
    with open('src/database/RegisteredSubject.csv', 'r', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        registered_data = []
        
        for row in csv_reader:
            grade = row['Grade'].strip() if row['Grade'].strip() else None
            registered_data.append((
                int(row['StudentID']),
                row['SubjectID'].strip(),  # เก็บเป็น TEXT เพื่อรักษาเลข 0 ข้างหน้า
                grade
            ))
    
    cursor.executemany('''
        INSERT INTO RegisteredSubject (StudentID, SubjectID, Grade)
        VALUES (?, ?, ?)
    ''', registered_data)
    
    print(f"Inserted {len(registered_data)} records into RegisteredSubject table")

def show_summary():
    """แสดงสรุปข้อมูลในฐานข้อมูล"""
    print("\n=== Database Summary ===")
    
    # นับจำนวนข้อมูลในแต่ละตาราง
    cursor.execute("SELECT COUNT(*) FROM Students")
    print(f"Students: {cursor.fetchone()[0]} records")
    
    cursor.execute("SELECT COUNT(*) FROM Subjects")
    print(f"Subjects: {cursor.fetchone()[0]} records")
    
    cursor.execute("SELECT COUNT(*) FROM SubjectStructure")
    print(f"SubjectStructure: {cursor.fetchone()[0]} records")
    
    cursor.execute("SELECT COUNT(*) FROM RegisteredSubject")
    print(f"RegisteredSubject: {cursor.fetchone()[0]} records")
    
    # แสดงข้อมูลตัวอย่าง
    print("\n=== Sample Data ===")
    cursor.execute("SELECT * FROM Students LIMIT 3")
    print("Students sample:", cursor.fetchall())
    
    cursor.execute("SELECT * FROM Subjects LIMIT 3")
    print("Subjects sample:", cursor.fetchall())

def main():
    """ฟังก์ชันหลัก"""
    print("Starting CSV to SQLite import process...")
    
    try:
        # ลบตารางเก่า
        drop_all_tables()
        
        # สร้างตารางใหม่
        print("\nCreating tables...")
        create_students_table()
        create_subjects_table()
        create_subject_structure_table()
        create_registered_subject_table()
        
        # โหลดข้อมูลจาก CSV files
        print("\nLoading data from CSV files...")
        load_students_csv()
        load_subjects_csv()
        load_subject_structure_csv()
        load_registered_subject_csv()
        
        # Commit การเปลี่ยนแปลง
        conn.commit()
        
        # แสดงสรุป
        show_summary()
        
        print(f"\n=== Success! ===")
        print(f"All CSV data has been imported to: {db_path}")
        
    except FileNotFoundError as e:
        print(f"Error: CSV file not found - {e}")
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()