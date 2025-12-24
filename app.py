from flask import Flask, render_template, request
from shad_checker import ShadChecker

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        token = request.form.get("token", "").strip()

        if not token:
            error = "توکن وارد نشده"
        else:
            checker = ShadChecker()
            result = checker.check_token(token)

    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
