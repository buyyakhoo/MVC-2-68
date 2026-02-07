import sys
import os
from flask import Flask, jsonify, request
from flask_cors import CORS  # ตัวช่วยให้ Frontend เรียก API ข้าม Port ได้
from datetime import datetime

# =========================================================
# IMPORT MODELS
# =========================================================
# ตรวจสอบ path เพื่อ import model
try:
    from model.politicians_model import PoliticiansModel
    from model.campaigns_model import CampaignsModel
    from model.promises_model import PromisesModel
    from model.promise_updates_model import PromiseUpdatesModel
except ImportError as e:
    print("Error Importing Models:", e)
    exit(1)

app = Flask(__name__)
# อนุญาตให้ทุกโดเมนเรียก API ได้ (จำเป็นสำหรับ Live Server Frontend)
CORS(app) 

# =========================================================
# INITIALIZE MODELS
# =========================================================
politicians_model = PoliticiansModel()
campaigns_model = CampaignsModel()
promises_model = PromisesModel()
updates_model = PromiseUpdatesModel()

# =========================================================
# 1. API: ดึงคำสัญญาทั้งหมด
# Endpoint: GET /api/promises
# =========================================================
@app.route('/api/promises', methods=['GET'])
def get_all_promises():
    try:
        # ดึงข้อมูล (Model return list of dict อยู่แล้ว)
        promises = promises_model.get_all_promises_with_politician_info()
        
        # ส่งกลับเป็น JSON
        return jsonify({
            "status": "success",
            "count": len(promises),
            "data": promises
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# =========================================================
# 2. API: ดูรายละเอียดคำสัญญา + ประวัติ
# Endpoint: GET /api/promises/<id>
# =========================================================
@app.route('/api/promises/<promise_id>', methods=['GET'])
def get_promise_detail(promise_id):
    # 1. ดึงข้อมูลสัญญา
    promise = promises_model.get_promise_detail_by_id(promise_id)
    
    if not promise:
        return jsonify({"status": "error", "message": "Promise not found"}), 404

    # 2. ดึงประวัติการอัปเดต
    updates = updates_model.get_updates_by_promise_id(promise_id)

    return jsonify({
        "status": "success",
        "data": {
            "promise": promise,
            "updates": updates
        }
    }), 200

# =========================================================
# 3. API: เพิ่มความคืบหน้า (POST JSON)
# Endpoint: POST /api/promises/<id>/updates
# =========================================================
@app.route('/api/promises/<promise_id>/updates', methods=['POST'])
def add_promise_update(promise_id):
    # 1. รับข้อมูล
    data = request.get_json()
    detail = data.get('detail')
    update_date_str = data.get('update_date') # รับมาเป็น String 'YYYY-MM-DD'
    new_status = data.get('status')

    if not update_date_str:
        update_date_str = datetime.now().strftime("%Y-%m-%d")

    # 2. ดึงข้อมูลสัญญามาตรวจสอบ
    promise = promises_model.get_promise_detail_by_id(promise_id)
    if not promise:
        return jsonify({"status": "error", "message": "Promise not found"}), 404

    # --- Check 1: ห้ามอัปเดตถ้า "เงียบหาย" ---
    if promise['status'] == 'เงียบหาย':
        return jsonify({"status": "error", "message": "Cannot update: Status is Silent"}), 400

    # --- Check 2: วันที่อัปเดต ต้องไม่ก่อน วันที่ประกาศ ---
    try:
        # แปลง String เป็น Object วันที่เพื่อเปรียบเทียบ
        announcement_date = datetime.strptime(promise['announcement_date'], "%Y-%m-%d")
        new_update_date = datetime.strptime(update_date_str, "%Y-%m-%d")

        if new_update_date < announcement_date:
            return jsonify({
                "status": "error", 
                "message": f"วันที่อัปเดต ({update_date_str}) ต้องไม่เกิดขึ้นก่อนวันที่ประกาศสัญญา ({promise['announcement_date']})"
            }), 400
            
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid date format"}), 400

    # --- Check 3: ต้องไม่ย้อนหลังไปกว่า "การอัปเดตล่าสุด" (Time Paradox)
    # 1. ดึงประวัติการอัปเดตทั้งหมดของสัญญานี้
    existing_updates = updates_model.get_updates_by_promise_id(promise_id)
    
    if existing_updates:
        # 2. หาวันที่ล่าสุดที่มีอยู่ในระบบ (สมมติว่าใน DB เก็บเป็น YYYY-MM-DD string)
        # ใช้ max() เพื่อหาค่าวันที่มากที่สุด
        latest_update_str = max(u['update_date'] for u in existing_updates)
        latest_update_date = datetime.strptime(latest_update_str, "%Y-%m-%d")

        # 3. เปรียบเทียบ
        if new_update_date < latest_update_date:
            return jsonify({
                "status": "error",
                "message": f"ไม่สามารถบันทึกได้: วันที่ระบุ ({update_date_str}) เกิดขึ้นก่อนการอัปเดตล่าสุด ({latest_update_str})"
            }), 400


    # 3. บันทึกข้อมูล (ถ้าผ่านทุกด่าน)
    if detail:
        # 3.1 บันทึกประวัติ (Update Log)
        success_log = updates_model.add_update(promise_id, detail, update_date_str)
        
        # 3.2 [เพิ่ม] อัปเดตสถานะสัญญา (ถ้ามีการส่งค่ามา และไม่ใช่ "same")
        success_status = True
        if new_status and new_status != 'same':
            success_status = promises_model.update_promise_status(promise_id, new_status)

        if success_log and success_status:
            return jsonify({
                "status": "success", 
                "message": "Update added and status changed"
            }), 201
        else:
            return jsonify({"status": "error", "message": "Database error"}), 500
    else:
        return jsonify({"status": "error", "message": "Detail is required"}), 400

# =========================================================
# 4. API: ข้อมูลนักการเมือง (Profile + Campaigns + Promises)
# Endpoint: GET /api/politicians/<id>
# =========================================================
@app.route('/api/politicians/<politician_id>', methods=['GET'])
def get_politician_profile(politician_id):
    # 1. ข้อมูลส่วนตัว
    profile = politicians_model.get_politician_by_id(politician_id)
    if not profile:
        return jsonify({"status": "error", "message": "Politician not found"}), 404

    # 2. ประวัติการหาเสียง
    campaigns = campaigns_model.get_campaigns_by_politician(politician_id)

    # 3. คำสัญญาของคนนี้
    promises = promises_model.get_promises_by_politician(politician_id)

    return jsonify({
        "status": "success",
        "data": {
            "profile": profile,
            "campaigns": campaigns,
            "promises": promises
        }
    }), 200

# =========================================================
# 5. API: รายชื่อนักการเมืองทั้งหมด
# Endpoint: GET /api/politicians
# =========================================================
@app.route('/api/politicians', methods=['GET'])
def get_politician_list():
    politicians = politicians_model.get_all_politicians()
    return jsonify({
        "status": "success",
        "count": len(politicians),
        "data": politicians
    }), 200

if __name__ == '__main__':
    # รันบน port 5000 (ค่า default)
    # Frontend จะ fetch ไปที่ http://localhost:5000/api/...
    print("🚀 Server running at http://localhost:5000")
    app.run(debug=True)