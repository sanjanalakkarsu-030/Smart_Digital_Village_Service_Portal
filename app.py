from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/citizen")
def citizen():
    return render_template("citizen.html")

@app.route("/complaints")
def complaints():
    return render_template("complaints.html")

@app.route("/government")
def government():
    return render_template("government.html")

@app.route("/announcements")
def announcements():
    return render_template("announcements.html")

@app.route("/agriculture")
def agriculture():
    return render_template("agriculture.html")

@app.route("/health")
def health():
    return render_template("health.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

if __name__ == "__main__":
    app.run(debug=True)