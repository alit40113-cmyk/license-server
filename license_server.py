from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

LICENSE_KEYS = {
    "INSTA-PRO-VIP": {"expires": None},
    "INSTA-USER-Alikhalaf": {"expires": "2026-1-19"}
}

@app.route("/check", methods=["POST"])
def check_license():
    data = request.get_json(force=True)
    key = data.get("key")

    if not key:
        return jsonify({"status": "fail", "reason": "no_key"}), 400

    if key not in LICENSE_KEYS:
        return jsonify({"status": "fail", "reason": "invalid"}), 403

    exp = LICENSE_KEYS[key]["expires"]
    if exp:
        if datetime.datetime.now() > datetime.datetime.fromisoformat(exp):
            return jsonify({"status": "fail", "reason": "expired"}), 403

    return jsonify({"status": "ok"}), 200

@app.route("/")
def home():
    return "License Server Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
