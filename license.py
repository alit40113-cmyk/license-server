from flask import Flask, request, jsonify
import datetime
import json
import os

app = Flask(__name__)
DB_FILE = "database.json"

# قائمة الأكواد مع تخصيص الوقت وعدد الأجهزة لكل واحد
LICENSES = [
    {
        "key": "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4", 
        "name": "Ali Khalaf (1234)",
        "expires": "2026-05-20T23:59:59",  # ينتهي في شهر 5
        "limit": 5                         # مسموح لـ 5 أجهزة فقط
    },
    {
        "key": "df7e70e5021544af483d1c28ef6169b1d227b3093200722a27e7cc1423405392", 
        "name": "User (0000)",
        "expires": "2026-12-31T23:59:59",  # ينتهي نهاية السنة
        "limit": 10000                     # عدد أجهزة مفتوح تقريباً
    },
    {
        "key": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8", 
        "name": "Guest (TEST)",
        "expires": "2026-02-15T12:00:00",  # ينتهي بعد يومين (تجريبي)
        "limit": 1                         # جهاز واحد فقط
    }
]

def get_hwid_file():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

@app.route("/check", methods=["POST"])
def check_license():
    data = request.get_json()
    if not data or "key" not in data:
        return jsonify({"status": "fail"}), 400
        
    user_hash = data.get("key")
    user_hwid = data.get("hwid", "unknown")
    
    # البحث عن الكود داخل المصفوفة
    found_license = None
    for lic in LICENSES:
        if lic["key"] == user_hash:
            found_license = lic
            break
            
    if found_license:
        # 1. فحص التاريخ الخاص بهذا الكود تحديداً
        expiry_date = datetime.datetime.strptime(found_license["expires"], "%Y-%m-%dT%H:%M:%S")
        if datetime.datetime.now() > expiry_date:
            return jsonify({"status": "fail", "reason": "expired"}), 403

        # 2. فحص الأجهزة بناءً على الـ limit الخاص بهذا الكود
        db = get_hwid_file()
        if user_hash not in db: db[user_hash] = []
        
        if user_hwid not in db[user_hash]:
            # نستخدم الـ limit المذكور في المصفوفة أعلاه
            if len(db[user_hash]) < found_license["limit"]:
                db[user_hash].append(user_hwid)
                with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)
            else:
                return jsonify({"status": "fail", "reason": "limit_reached"}), 403

        # الاستجابة بالبيانات المخصصة
        return jsonify({
            "status": "ok", 
            "expires": found_license["expires"], 
            "user": found_license["name"]
        }), 200
    
    return jsonify({"status": "fail", "reason": "invalid"}), 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
