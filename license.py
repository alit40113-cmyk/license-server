from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

# ضع هاش الأكواد هنا (SHA256)
LICENSE_KEYS = {
    "8d61e185a95398438e4433984feb90ebe774b1a5b32dcff75479037831462a6f": {
        "name": "Atheer",
        "expires": "2026-05-01T00:00:00",
        "limit": 2000,
        "hwids": []
    }
}

@app.route("/check", methods=["POST"])
def check_license():
    data = request.get_json()
    key = data.get("key")
    hwid = data.get("hwid")
    
    if key not in LICENSE_KEYS:
        return jsonify({"status": "fail", "reason": "invalid"}), 403
    
    lic = LICENSE_KEYS[key]
    if datetime.datetime.now() > datetime.datetime.fromisoformat(lic["expires"]):
        return jsonify({"status": "fail", "reason": "expired"}), 403

    if hwid not in lic["hwids"]:
        if len(lic["hwids"]) < lic["limit"]:
            lic["hwids"].append(hwid)
        else:
            return jsonify({"status": "fail", "reason": "limit_reached"}), 403

    return jsonify({"status": "ok", "expires": lic["expires"]}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
