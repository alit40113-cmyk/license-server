from flask import Flask, request, jsonify
import sys

app = Flask(__name__)

@app.route("/check", methods=["POST"])
def check_license():
    data = request.get_json()
    user_hash = data.get("key", "No Key Found")
    
    # هذه السطور ستجبر السيرفر على طباعة الهاش في الـ Logs مهما كان السبب
    print("\n" + "!"*60, flush=True)
    print(f"!!! THE HASH YOU NEED IS: {user_hash} !!!", flush=True)
    print("!"*60 + "\n", flush=True)
    
    # لضمان ظهورها في بعض الاستضافات
    sys.stdout.flush()

    return jsonify({
        "status": "ok", 
        "expires": "2026-12-31T23:59:59", 
        "user": "SEE LOGS FOR HASH"
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
