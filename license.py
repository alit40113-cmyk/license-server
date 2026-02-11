from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

# قاعدة بيانات المفاتيح (أضف مفاتيحك هنا)
# المفتح يكون عبارة عن SHA256 Hash للكود الذي يعطى للمستخدم
LICENSE_KEYS = {
    "8d61e185a95398438e4433984feb90ebe774b1a5b32dcff75479037831462a6f": {
        "name": "Atheer",
        "expires": "2026-05-01",
        "limit": 2000,
        "hwids": []
    },
    "4a193ebe299bcd9a10f8a0d70126b4865f045bf274aee320f48666d672b058fd": {
        "name": "User_2",
        "expires": "2026-03-15",
        "limit": 1000,
        "hwids": []
    }
}

@app.route("/check", methods=["POST"])
def check_license():
    data = request.get_json(force=True)
    key = data.get("key") # الكود مشفر
    hwid = data.get("hwid")

    if key not in LICENSE_KEYS:
        return jsonify({"status": "fail", "reason": "invalid"}), 403

    lic = LICENSE_KEYS[key]
    
    # فحص التاريخ
    exp_date = datetime.datetime.fromisoformat(lic["expires"])
    if datetime.datetime.now() > exp_date:
        return jsonify({"status": "fail", "reason": "expired"}), 403

    # فحص الأجهزة (الـ HWID)
    if hwid not in lic["hwids"]:
        if len(lic["hwids"]) < lic["limit"]:
            lic["hwids"].append(hwid) # تسجيل الجهاز الجديد تلقائياً
        else:
            return jsonify({"status": "fail", "reason": "limit_reached"}), 403

    return jsonify({
        "status": "ok", 
        "name": lic["name"], 
        "expires": lic["expires"]
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
