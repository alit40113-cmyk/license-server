from flask import Flask, request, jsonify
import datetime
import json
import os

app = Flask(__name__)

DB_FILE = "database.json"

# الدالة المسؤولة عن تحميل البيانات من الملف
def load_db():
    if not os.path.exists(DB_FILE):
        # البيانات الأولية إذا كان الملف غير موجود
        initial_db = {
            "8d61e185a95398438e4433984feb90ebe774b1a5b32dcff75479037831462a6f": {
                "name": "Atheer",
                "expires": "2026-12-31T00:00:00",
                "limit": 1,
                "hwids": []
            }
        }
        save_db(initial_db)
        return initial_db
    with open(DB_FILE, "r") as f:
        return json.load(f)

# الدالة المسؤولة عن حفظ البيانات في الملف
def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/check", methods=["POST"])
def check_license():
    db = load_db()  # قراءة البيانات الحالية
    data = request.get_json()
    key = data.get("key")
    hwid = data.get("hwid")
    
    if key not in db:
        return jsonify({"status": "fail", "reason": "invalid"}), 403
    
    lic = db[key]
    
    # فحص تاريخ الانتهاء
    if datetime.datetime.now() > datetime.datetime.fromisoformat(lic["expires"]):
        return jsonify({"status": "fail", "reason": "expired"}), 403

    # فحص الـ HWID والحفظ إذا كان جديداً
    if hwid not in lic["hwids"]:
        if len(lic["hwids"]) < lic["limit"]:
            lic["hwids"].append(hwid)
            save_db(db)  # حفظ التغيير فوراً في الملف
        else:
            return jsonify({"status": "fail", "reason": "limit_reached"}), 403

    return jsonify({"status": "ok", "expires": lic["expires"]}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
