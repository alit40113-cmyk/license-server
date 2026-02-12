from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/check", methods=["POST"])
def check_license():
    data = request.get_json()
    user_hash = data.get("key", "No Key")
    
    # سنرسل الهاش كأنه "اسم المستخدم" لكي تراه في الأداة
    return jsonify({
        "status": "ok", 
        "expires": "2026-12-31T23:59:59", 
        "user": f"HASH IS: {user_hash}"
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
