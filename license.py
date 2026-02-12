from flask import Flask, request, jsonify
import datetime
import json
import os

app = Flask(__name__)
DB_FILE = "database.json"

def get_keys_data():
    # قائمة الأكواد: أضف أي كود جديد هنا بنفس التنسيق
    return [
        {
            "hash": "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4",
            "name": "Ali Khalaf (1234)",
            "expires": "2026-12-31T23:59:59",
            "limit": 10000
        },
        {
            "hash": "df7e70e5021544af483d1c28ef6169b1d227b3093200722a27e7cc1423405392",
            "name": "User (0000)",
            "expires": "2026-12-31T23:59:59",
            "limit": 10000
        },
        {
            "hash": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
            "name": "Guest (TEST)",
            "expires": "2026-12-31T23:59:59",
            "limit": 10000
        }
    ]

def load_and_sync_db():
    required_keys = get_keys_data()
    db = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                db = json.load(f)
        except: db = {}

    # تحديث أو إضافة كل كود موجود في القائمة أعلاه
    for item in required_keys:
        h = item["hash"]
        if h not in db:
            db[h] = {
                "name": item["name"],
                "expires": item["expires"],
                "limit": item["limit"],
                "hwids": []
            }
        else:
            # تحديث البيانات الأساسية فقط مع الحفاظ على الأجهزة المسجلة
            db[h]["name"] = item["name"]
            db[h]["expires"] = item["expires"]
            db[h]["limit"] = item["limit"]
            if "hwids" not in db[h]: db[h]["hwids"] = []

    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)
    return db

@app.route("/check", methods=["POST"])
def check_license():
    db = load_and_sync_db()
    data = request.get_json()
    
    if not data or "key" not in data:
        return jsonify({"status": "fail", "reason": "no_data"}), 400
        
    user_hash = data.get("key")
    user_hwid = data.get("hwid", "unknown")
    
    print(f"[*] Checking Key: {user_hash}")

    # فحص الكود في قاعدة البيانات
    if user_hash in db:
        lic = db[user_hash]
        
        # 1. فحص التاريخ
        expiry = datetime.datetime.strptime(lic["expires"], "%Y-%m-%dT%H:%M:%S")
        if datetime.datetime.now() > expiry:
            return jsonify({"status": "fail", "reason": "expired"}), 403

        # 2. فحص الأجهزة
        if user_hwid not in lic["hwids"]:
            if len(lic["hwids"]) < lic["limit"]:
                lic["hwids"].append(user_hwid)
                with open(DB_FILE, "w") as f:
                    json.dump(db, f, indent=4)
            else:
                return jsonify({"status": "fail", "reason": "limit_reached"}), 403

        # نجاح التفعيل
        return jsonify({
            "status": "ok", 
            "expires": lic["expires"], 
            "user": lic["name"]
        }), 200
    
    # إذا لم يتم العثور على الهاش
    print(f"[-] Key not found in Database!")
    return jsonify({"status": "fail", "reason": "invalid"}), 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
