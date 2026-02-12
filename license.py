from flask import Flask, request, jsonify
import datetime
import json
import os
import hashlib

app = Flask(__name__)

DB_FILE = "database.json"

# الدالة المسؤولة عن تحميل البيانات من الملف أو إنشائها لأول مرة
def load_db():
    if not os.path.exists(DB_FILE):
        # هنا تضيف كل المفاتيح التي تريدها (أضفت لك 3 أمثلة)
        initial_db = {
            # مفتاح 1: 1234
            "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4": {
                "name": "Ali Khalaf",
                "expires": "2026-12-31T23:59:59",
                "limit": 10,
                "hwids": []
            },
            # مفتاح 2: VIP-Atheer-2025
            "f9485746352b21c43d546271a5398438e4433984feb90ebe774b1a5b32dcff75": {
                "name": "Atheer",
                "expires": "2026-12-31T23:59:59",
                "limit": 1,
                "hwids": []
            },
            # مفتاح 3: TEST-FREE-555
            "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8": {
                "name": "Guest User",
                "expires": "2026-02-28T23:59:59",
                "limit": 5, # يسمح لـ 5 أجهزة مختلفة
                "hwids": []
            }
        }
        save_db(initial_db)
        return initial_db
    
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

# الدالة المسؤولة عن حفظ البيانات في الملف
def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/check", methods=["POST"])
def check_license():
    db = load_db()  # قراءة قاعدة البيانات
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "fail", "reason": "no_data"}), 400
        
    key = data.get("key")
    hwid = data.get("hwid")
    
    # 1. فحص هل المفتاح موجود أصلاً؟
    if key not in db:
        return jsonify({"status": "fail", "reason": "invalid"}), 403
    
    lic = db[key]
    
    # 2. فحص هل المفتاح منتهي الصلاحية؟
    expiry_date = datetime.datetime.fromisoformat(lic["expires"])
    if datetime.datetime.now() > expiry_date:
        return jsonify({"status": "fail", "reason": "expired"}), 403

    # 3. فحص بصمة الجهاز (HWID)
    if hwid not in lic["hwids"]:
        # إذا كان جهاز جديد، نتحقق هل وصل للحد المسموح (Limit)؟
        if len(lic["hwids"]) < lic["limit"]:
            lic["hwids"].append(hwid)
            save_db(db)  # حفظ الجهاز الجديد في قاعدة البيانات
        else:
            # تم الوصول للحد الأقصى من الأجهزة لهذا المفتاح
            return jsonify({"status": "fail", "reason": "limit_reached"}), 403

    # إذا مر كل شيء بسلام
    return jsonify({
        "status": "ok", 
        "expires": lic["expires"],
        "user": lic["name"]
    }), 200

if __name__ == "__main__":
    # تشغيل السيرفر على جميع الواجهات بالبورت 5000
    app.run(host="0.0.0.0", port=5000)
