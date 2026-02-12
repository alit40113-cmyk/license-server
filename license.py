from flask import Flask, request, jsonify
import datetime
import json
import os
import hashlib

app = Flask(__name__)

DB_FILE = "database.json"

def load_db():
    # الأكواد الجديدة التي تريد فرضها (سيتم مسح بياناتها القديمة وتحديثها)
    required_keys = {
        "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4": {
            "name": "Ali Khalaf (1234)",
            "expires": "2026-12-31T23:59:59",
            "limit": 10000,
            "hwids": [] # تصفير الأجهزة المسجلة سابقاً
        },
        "df7e70e5021544af483d1c28ef6169b1d227b3093200722a27e7cc1423405392": {
            "name": "New User (0000)",
            "expires": "2026-12-31T23:59:59",
            "limit": 1000,
            "hwids": []
        },
        "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8": {
            "name": "Guest User (TEST)",
            "expires": "2026-12-31T23:59:59",
            "limit": 5000,
            "hwids": []
        }
    }

    db = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                db = json.load(f)
            except:
                db = {}

    # استبدال بيانات الأكواد القديمة بالبيانات الجديدة (Update/Overwrite)
    for k, v in required_keys.items():
        db[k] = v 
    
    save_db(db)
    return db

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/check", methods=["POST"])
def check_license():
    db = load_db()
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "fail", "reason": "no_data"}), 400
        
    key = data.get("key")
    hwid = data.get("hwid")
    
    print(f"\n[?] Request: {key}")

    if key not in db:
        print(f"[-] Invalid Key")
        return jsonify({"status": "fail", "reason": "invalid"}), 403
    
    lic = db[key]
    
    # فحص التاريخ
    expiry_date = datetime.datetime.strptime(lic["expires"], "%Y-%m-%dT%H:%M:%S")
    if datetime.datetime.now() > expiry_date:
        return jsonify({"status": "fail", "reason": "expired"}), 403

    # فحص الأجهزة
    if hwid not in lic["hwids"]:
        if len(lic["hwids"]) < lic["limit"]:
            lic["hwids"].append(hwid)
            save_db(db)
            print(f"[+] Device Registered: {hwid}")
        else:
            return jsonify({"status": "fail", "reason": "limit_reached"}), 403

    return jsonify({
        "status": "ok", 
        "expires": lic["expires"],
        "user": lic["name"]
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
