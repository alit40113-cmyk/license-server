from flask import Flask, request, jsonify
import datetime
import json
import os

app = Flask(__name__)

DB_FILE = "database.json"

def get_keys():
    # هنا تضع كل الأكواد التي تريدها
    # أي كود تضعه هنا سيعمل فوراً
    return {
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

def load_db():
    keys = get_keys()
    db = {}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                db = json.load(f)
        except:
            db = {}
    
    # تحديث البيانات من get_keys إلى الملف دون مسح الأجهزة المسجلة
    for k, v in keys.items():
        if k not in db:
            db[k] = v
            db[k]["hwids"] = []
        else:
            # تحديث التاريخ والاسم والحد فقط
            db[k].update({"name": v["name"], "expires": v["expires"], "limit": v["limit"]})
            if "hwids" not in db[k]: db[k]["hwids"] = []
            
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)
    return db

@app.route("/check", methods=["POST"])
def check_license():
    db = load_db()
    data = request.get_json()
    
    if not data or "key" not in data:
        return jsonify({"status": "fail", "reason": "no_data"}), 400
        
    user_key = data.get("key")
    hwid = data.get("hwid", "unknown")
    
    print(f"[*] Request for Key: {user_key}")

    # الفحص: هل الهاش موجود في أي مكان داخل قاعدة البيانات؟
    if user_key in db:
        lic = db[user_key]
        
        # فحص التاريخ
        expiry = datetime.datetime.strptime(lic["expires"], "%Y-%m-%dT%H:%M:%S")
        if datetime.datetime.now() > expiry:
            return jsonify({"status": "fail", "reason": "expired"}), 403

        # فحص الأجهزة
        if hwid not in lic["hwids"]:
            if len(lic["hwids"]) < lic["limit"]:
                lic["hwids"].append(hwid)
                with open(DB_FILE, "w") as f:
                    json.dump(db, f, indent=4)
            else:
                return jsonify({"status": "fail", "reason": "limit_reached"}), 403

        return jsonify({
            "status": "ok", 
            "expires": lic["expires"], 
            "user": lic["name"]
        }), 200
    
    # إذا لم يجد الكود في كل القاموس
    print(f"[-] Key {user_key} not found!")
    return jsonify({"status": "fail", "reason": "invalid"}), 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
