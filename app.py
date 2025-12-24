from flask import Flask, request, jsonify
from shad_checker import ShadChecker

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "SHAD TOKEN CHECKER IS RUNNING"

@app.route("/check", methods=["POST"])
def check():
    data = request.get_json()
    token = data.get("token", "").strip()

    if not token:
        return jsonify({"error": "token missing"}), 400

    checker = ShadChecker()
    result = checker.check_token(token)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
