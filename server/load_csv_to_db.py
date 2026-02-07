import sqlite3
import csv
import os

# --- ตั้งค่า Path และชื่อไฟล์ ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FOLDER = os.path.join(BASE_DIR, "src", "database")
DB_PATH = os.path.join(DB_FOLDER, "political_party.db")

# สร้างโฟลเดอร์ src/database ถ้ายังไม่มี
os.makedirs(DB_FOLDER, exist_ok=True)

def clean_old_db():
    """ลบ Database เก่าทิ้งเพื่อเริ่มใหม่แบบ Clean"""
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print(f"Removed old database at: {DB_PATH}")
        except PermissionError:
            print("Error: ไม่สามารถลบไฟล์ Database เก่าได้ (อาจมีโปรแกรมอื่นเปิดอยู่)")
            return False
    return True

def get_csv_path(filename):
    """หาไฟล์ CSV จากทั้งโฟลเดอร์ปัจจุบันและโฟลเดอร์ src/database"""
    # 1. ลองหาในโฟลเดอร์เดียวกับ script
    path1 = os.path.join(BASE_DIR, filename)
    if os.path.exists(path1): return path1
    
    # 2. ลองหาในโฟลเดอร์ database
    path2 = os.path.join(DB_FOLDER, filename)
    if os.path.exists(path2): return path2
    
    return None

def create_tables(conn):
    cursor = conn.cursor()
    
    # 1. Politicians
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Politicians (
            politician_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            party TEXT NOT NULL
        )
    ''')

    # 2. Campaigns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Campaigns (
            campaign_id TEXT PRIMARY KEY,
            politician_id TEXT NOT NULL,
            election_year INTEGER NOT NULL,
            district TEXT NOT NULL,
            FOREIGN KEY (politician_id) REFERENCES Politicians(politician_id)
        )
    ''')

    # 3. Promises
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Promises (
            promise_id TEXT PRIMARY KEY,
            politician_id TEXT NOT NULL,
            description TEXT NOT NULL,
            announcement_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (politician_id) REFERENCES Politicians(politician_id)
        )
    ''')

    # 4. PromiseUpdates (ตัวที่มีปัญหา)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS PromiseUpdates (
            update_id TEXT PRIMARY KEY,
            promise_id TEXT NOT NULL,
            update_date TEXT NOT NULL,
            detail TEXT NOT NULL,
            FOREIGN KEY (promise_id) REFERENCES Promises(promise_id)
        )
    ''')
    conn.commit()
    print("Created all tables successfully.")

def import_csv_data(conn):
    cursor = conn.cursor()
    
    # รายชื่อไฟล์และการ mapping (ชื่อไฟล์จริงในเครื่องต้องตรงกับ key ใน dict นี้)
    files_map = {
        "politicians.csv": { # หรือ Politicians.csv
            "table": "Politicians",
            "cols": ["politician_id", "name", "party"]
        },
        "campaigns.csv": {
            "table": "Campaigns",
            "cols": ["campaign_id", "politician_id", "election_year", "district"]
        },
        "promises.csv": {
            "table": "Promises",
            "cols": ["promise_id", "politician_id", "description", "announcement_date", "status"]
        },
        "promise_updates.csv": { # ตรวจสอบชื่อไฟล์นี้ให้ดี
            "table": "PromiseUpdates",
            "cols": ["update_id", "promise_id", "update_date", "detail"]
        }
    }

    print("\n--- Starting Data Import ---")
    
    for filename, config in files_map.items():
        filepath = get_csv_path(filename)
        
        # ถ้าไม่เจอ ลองหาแบบ Case Insensitive (เผื่อชื่อไฟล์ตัวเล็กตัวใหญ่ไม่ตรง)
        if not filepath:
            # ลองหาไฟล์ที่มีชื่อคล้ายกันในโฟลเดอร์
            for f in os.listdir(BASE_DIR):
                if f.lower() == filename.lower():
                    filepath = os.path.join(BASE_DIR, f)
                    break
        
        if not filepath:
            print(f"❌ Error: หาไฟล์ '{filename}' ไม่เจอ! (ข้ามการ import ตาราง {config['table']})")
            continue

        print(f"Reading {os.path.basename(filepath)}...")
        
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                # Normalize headers: ลบช่องว่างหัวท้ายชื่อคอลัมน์
                reader.fieldnames = [name.strip() for name in reader.fieldnames]
                
                data_list = []
                for row in reader:
                    # ดึงข้อมูลโดยใช้ .get() เพื่อป้องกัน Error ถ้าชื่อ column ใน csv ไม่ตรงเป๊ะ
                    # และ strip() ข้อมูลเพื่อลบช่องว่างส่วนเกิน
                    record = [row.get(col, '').strip() for col in config['cols']]
                    
                    # เช็คว่ามีข้อมูลครบไหม (ถ้าเป็นค่าว่างทั้งหมดแสดงว่าเป็นบรรทัดเปล่า)
                    if any(record):
                        data_list.append(record)

                if data_list:
                    placeholders = ','.join(['?'] * len(config['cols']))
                    sql = f"INSERT INTO {config['table']} ({','.join(config['cols'])}) VALUES ({placeholders})"
                    cursor.executemany(sql, data_list)
                    print(f"  ✅ Imported {len(data_list)} records into {config['table']}")
                else:
                    print(f"  ⚠️ No data found in file")

        except Exception as e:
            print(f"  ❌ Error importing {filename}: {e}")

    conn.commit()

def verify_data(conn):
    cursor = conn.cursor()
    print("\n--- Verifying Data ---")
    tables = ["Politicians", "Campaigns", "Promises", "PromiseUpdates"]
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count} records")
        except sqlite3.OperationalError:
            print(f"{table}: Table not found!")

def main():
    if not clean_old_db():
        return

    print(f"Creating database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    try:
        create_tables(conn)
        import_csv_data(conn)
        verify_data(conn)
        print("\n=== Process Completed ===")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()