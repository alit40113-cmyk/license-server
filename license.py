from flask import Flask, request, jsonify
import datetime
import json
import os

app = Flask(__name__)
DB_FILE = "database.json"

# هذه هي "القائمة الذهبية" - السيرفر سيعترف بهذه الأكواد فقط
KEYS_DATA = {
    "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4": {
        "name": "Ali Khalaf (1234)", "expires": "2026-12-31T23:59:59", "limit": 10000
    },
    "df7e70e5021544af483d1c28ef6169b1d227b3093200722a27e7cc1423405392": {
        "name": "User (0000)", "expires": "2026-12-31T23:59:59", "limit": 10000
    },
    "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8": {
        "name": "Guest (TEST)", "expires": "2026-12-31T23:59:59", "limit": 10000
    }
}

def get_hwids_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def save_hwids_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

@app.route("/check", methods=["POST"])
def check_license():
    data = request.get_json()
    if not data or "key" not in data:
        return jsonify({"status": "fail", "reason": "no_data"}), 400
        
    user_hash = data.get("key")
    user_hwid = data.get("hwid", "unknown")
    
    # الفحص المباشر من KEYS_DATA وليس من الملف
    if user_hash in KEYS_DATA:
        lic_info = KEYS_DATA[user_hash]
        
        # 1. فحص التاريخ
        expiry = datetime.datetime.strptime(lic_info["expires"], "%Y-%m-%dT%H:%M:%S")
        if datetime.datetime.now() > expiry:
            return jsonify({"status": "fail", "reason": "expired"}), 403

        # 2. فحص الأجهزة من ملف الـ HWIDs
        hwids_db = get_hwids_db()
        if user_hash not in hwids_db:
            hwids_db[user_hash] = []
        
        if user_hwid not in hwids_db[user_hash]:
            if len(hwids_db[user_hash]) < lic_info["limit"]:
                hwids_db[user_hash].append(user_hwid)
                save_hwids_db(hwids_db)
            else:
                return jsonify({"status": "fail", "reason": "limit_reached"}), 403

        return jsonify({
            "status": "ok", 
            "expires": lic_info["expires"], 
            "user": lic_info["name"]
        }), 200
    
    # إذا لم يجد الهاش في KEYS_DATA
    return jsonify({"status": "fail", "reason": "invalid"}), 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
