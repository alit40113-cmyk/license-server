from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/check", methods=["POST"])
def check_license():
    data = request.get_json()
    user_hash = data.get("key", "No Key")
    
    # هذه الرسالة ستظهر في شاشة السيرفر السوداء (Logs)
    print("\n" + "="*50)
    print(f"RECEIVED HASH: {user_hash}")
    print("="*50 + "\n")
    
    # سنقوم بجعل السيرفر يوافق على أي كود مؤقتاً لكي لا تتوقف الأداة
    return jsonify({
        "status": "ok", 
        "expires": "2026-12-31T23:59:59", 
        "user": "Scanner Mode"
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
