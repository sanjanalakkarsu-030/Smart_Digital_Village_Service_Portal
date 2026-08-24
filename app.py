from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import random
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "digital_village_secret_key")

# ---------------------------------
# MySQL Database Configuration
# ---------------------------------
app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST", "localhost")
app.config["MYSQL_USER"] = os.getenv("MYSQL_USER", "root")
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD", "")
app.config["MYSQL_DB"] = os.getenv("MYSQL_DB", "digital_village_service_portal")

mysql = MySQL(app)
bcrypt = Bcrypt(app)

# ---------------------------------
# Gmail SMTP Configuration
# ---------------------------------
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "your_email@gmail.com")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "your_app_password")
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]

mail = Mail(app)

# ---------------------------------
# Main Pages
# ---------------------------------

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

# ---------------------------------
# Authentication Pages
# ---------------------------------

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------------------------------
# Registration
# ---------------------------------

@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    full_name = data.get("full_name")
    mobile_number = data.get("mobile_number")
    house_number = data.get("house_number")
    ward_number = data.get("ward_number")
    gender = data.get("gender")
    email = data.get("email")
    address = data.get("address")
    username = data.get("username")
    password = data.get("password")

    if not all([full_name, mobile_number, house_number, ward_number, gender, email, address, username, password]):
        return jsonify({
            "success": False,
            "message": "All fields are required."
        })

    # Check if username already exists
    cur = mysql.connection.cursor()
    cur.execute("SELECT citizen_id FROM citizens WHERE username = %s", (username,))
    existing_user = cur.fetchone()

    if existing_user:
        cur.close()
        return jsonify({
            "success": False,
            "message": "Username already exists. Please choose a different username."
        })

    # Check if email already exists
    cur.execute("SELECT citizen_id FROM citizens WHERE email = %s", (email,))
    existing_email = cur.fetchone()

    if existing_email:
        cur.close()
        return jsonify({
            "success": False,
            "message": "Email already registered. Please login or use a different email."
        })

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    try:
        cur.execute(
            """INSERT INTO citizens 
               (full_name, mobile_number, house_number, ward_number, gender, email, address, username, password, registration_date, account_status) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (full_name, mobile_number, house_number, ward_number, gender, email, address, username, hashed_password, date.today(), "Active")
        )
        mysql.connection.commit()
        cur.close()

        return jsonify({
            "success": True,
            "message": "Registration successful!"
        })

    except Exception as e:
        cur.close()
        return jsonify({
            "success": False,
            "message": f"Registration failed: {str(e)}"
        })

# ---------------------------------
# Login
# ---------------------------------

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Username and password are required."
        })

    cur = mysql.connection.cursor()
    cur.execute("SELECT citizen_id, full_name, username, password, account_status FROM citizens WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()

    if not user:
        return jsonify({
            "success": False,
            "message": "Invalid username or password."
        })

    citizen_id, full_name, db_username, hashed_password, account_status = user

    if account_status != "Active":
        return jsonify({
            "success": False,
            "message": "Your account is inactive. Please contact the Gram Panchayat office."
        })

    if bcrypt.check_password_hash(hashed_password, password):
        session["citizen_id"] = citizen_id
        session["username"] = db_username
        session["full_name"] = full_name

        return jsonify({
            "success": True,
            "message": "Login successful!"
        })

    return jsonify({
        "success": False,
        "message": "Invalid username or password."
    })

# ---------------------------------
# Forgot Password Pages
# ---------------------------------

@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot_password.html")


@app.route("/verify-otp")
def verify_otp_page():
    return render_template("verify_otp.html")


@app.route("/reset-password")
def reset_password():
    return render_template("reset_password.html")


# ---------------------------------
# Send OTP
# ---------------------------------

@app.route("/send-otp", methods=["POST"])
def send_otp():

    data = request.get_json()

    email = data.get("email")

    if not email:
        return jsonify({
            "success": False,
            "message": "Email is required."
        })

    # Check if email exists in the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT citizen_id, full_name FROM citizens WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()

    if not user:
        return jsonify({
            "success": False,
            "message": "This email is not registered. Please check your email or register first."
        })

    citizen_id, full_name = user

    otp = str(random.randint(100000, 999999))

    session["otp"] = otp
    session["email"] = email

    try:
        msg = Message(
            subject="Smart Digital Village - Password Reset OTP",
            recipients=[email]
        )

        msg.body = f"""
Hello {full_name},

You have requested to reset your password for your Smart Digital Village Service Portal account.

Your One-Time Password (OTP) is:

{otp}

This OTP is valid for 10 minutes.

Do not share this OTP with anyone.

If you did not request this, please ignore this email.

Regards,
Smart Digital Village Service Portal Team
"""

        mail.send(msg)

        return jsonify({
            "success": True,
            "message": "OTP sent successfully to your email."
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to send OTP: {str(e)}"
        })


# ---------------------------------
# Verify OTP
# ---------------------------------

@app.route("/verify-otp", methods=["POST"])
def verify_otp():

    data = request.get_json()

    otp = data.get("otp")

    if otp == session.get("otp"):

        return jsonify({
            "success": True
        })

    return jsonify({
        "success": False,
        "message": "Invalid OTP."
    })


# ---------------------------------
# Update Password
# ---------------------------------

@app.route("/update-password", methods=["POST"])
def update_password():

    data = request.get_json()

    password = data.get("password")
    email = session.get("email")

    if not password:
        return jsonify({
            "success": False,
            "message": "Password is required."
        })

    if not email:
        return jsonify({
            "success": False,
            "message": "Session expired. Please try again."
        })

    # Hash the new password
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    try:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE citizens SET password = %s WHERE email = %s", (hashed_password, email))
        mysql.connection.commit()
        cur.close()

        # Clear the OTP session
        session.pop("otp", None)
        session.pop("email", None)

        return jsonify({
            "success": True,
            "message": "Password updated successfully. Please login with your new password."
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to update password: {str(e)}"
        })


# ---------------------------------
# Run Flask
# ---------------------------------

if __name__ == "__main__":
    app.run(debug=True)