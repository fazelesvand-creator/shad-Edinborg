import os
from flask import Flask, request, render_template_string, jsonify

app = Flask(__name__)

HTML_FORM = """
<!doctype html>
<html lang="fa">
<head>
  <meta charset="utf-8">
  <title>SHAD Token Checker</title>
  <style>
    body { font-family: sans-serif; background:#f5f5f5; padding:30px; }
    .box { max-width:400px; margin:auto; background:#fff; padding:20px; border-radius:8px; }
    input, button { width:100%; padding:10px; margin-top:10px; }
    button { background:#4CAF50; color:white; border:none; }
  </style>
</head>
<body>
  <div class="box">
    <h3>بررسی توکن شاد</h3>
    <form method="post" action="/check">
      <input name="token" placeholder="توکن را وارد کنید" required>
      <button type="submit">بررسی</button>
    </form>
  </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return HTML_FORM

@app.route("/check", methods=["POST"])
def check_token():
    token = request.form.get("token") or request.json.get("token")

    if not token or len(token) < 20:
        return jsonify({
            "status": "invalid",
            "message": "توکن نامعتبر است"
        })

    # نمونه خروجی (Mock / Demo)
    return jsonify({
        "status": "ok",
        "data": {
            "first_name": "نمونه",
            "last_name": "کاربر",
            "role": "دانش‌آموز",
            "mobile": "09*********"
        }
    })

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
