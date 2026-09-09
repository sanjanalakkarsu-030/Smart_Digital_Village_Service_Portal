from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import secrets
import os
import re
from datetime import date, datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

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
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", "587"))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "")
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


def json_body():
    return request.get_json(silent=True) or {}


def valid_email(email):
    return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email or ""))


def error_response(message, status=400):
    return jsonify({"success": False, "message": message}), status

# ---------------------------------
# Registration
# ---------------------------------

@app.route("/register", methods=["POST"])
def register():

    data = json_body()

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
        return error_response("All fields are required.")

    if not valid_email(email):
        return error_response("Please enter a valid email address.")

    # Check if username already exists
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT citizen_id FROM citizens WHERE username = %s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            return error_response("Username already exists. Please choose a different username.", 409)

        # Check if email already exists
        cur.execute("SELECT citizen_id FROM citizens WHERE email = %s", (email,))
        existing_email = cur.fetchone()

        if existing_email:
            cur.close()
            return error_response("Email already registered. Please login or use a different email.", 409)

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

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
        }), 201

    except Exception as e:
        app.logger.exception("Registration failed")
        return error_response("Database service is unavailable. Check MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DB in .env.", 503)

# ---------------------------------
# Login
# ---------------------------------

@app.route("/login", methods=["POST"])
def login():

    data = json_body()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return error_response("Username and password are required.")

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT citizen_id, full_name, username, password, account_status FROM citizens WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
    except Exception:
        app.logger.exception("Login database query failed")
        return error_response("Database service is unavailable. Check MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DB in .env.", 503)

    if not user:
        return error_response("Invalid username or password.", 401)

    citizen_id, full_name, db_username, hashed_password, account_status = user

    if account_status != "Active":
        return error_response("Your account is inactive. Please contact the Gram Panchayat office.", 403)

    if bcrypt.check_password_hash(hashed_password, password):
        session["citizen_id"] = citizen_id
        session["username"] = db_username
        session["full_name"] = full_name

        return jsonify({
            "success": True,
            "message": "Login successful!"
        })

    return error_response("Invalid username or password.", 401)

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

    data = json_body()

    email = data.get("email")

    if not email:
        return error_response("Email is required.")

    if not valid_email(email):
        return error_response("Please enter a valid email address.")

    # Check if email exists in the database
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT citizen_id, full_name FROM citizens WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
    except Exception:
        app.logger.exception("Forgot-password database query failed")
        return error_response("Database service is unavailable. Check MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DB in .env.", 503)

    if not user:
        return error_response("This email is not registered. Please check your email or register first.", 404)

    citizen_id, full_name = user

    if not app.config["MAIL_USERNAME"] or not app.config["MAIL_PASSWORD"]:
        app.logger.error("SMTP is not configured: MAIL_USERNAME and MAIL_PASSWORD are required")
        return error_response("Email service is not configured. Set MAIL_USERNAME and MAIL_PASSWORD in .env.", 503)

    otp = str(secrets.randbelow(900000) + 100000)

    session["otp"] = otp
    session["email"] = email
    session["otp_created_at"] = datetime.now(timezone.utc).isoformat()
    session["otp_verified"] = False

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

    except Exception:
        app.logger.exception("SMTP OTP delivery failed")
        session.pop("otp", None)
        session.pop("otp_created_at", None)
        session.pop("otp_verified", None)
        return error_response("Unable to send the OTP. Check the SMTP settings and try again.", 502)


# ---------------------------------
# Verify OTP
# ---------------------------------

@app.route("/verify-otp", methods=["POST"])
def verify_otp():

    data = json_body()

    otp = data.get("otp")
    created_at = session.get("otp_created_at")
    try:
        is_expired = not created_at or datetime.now(timezone.utc) - datetime.fromisoformat(created_at) > timedelta(minutes=10)
    except ValueError:
        is_expired = True

    if is_expired:
        return error_response("This OTP has expired. Please request a new one.", 410)

    if otp and secrets.compare_digest(str(otp), str(session.get("otp", ""))):
        session["otp_verified"] = True

        return jsonify({
            "success": True
        })

    return error_response("Invalid OTP.", 401)


# ---------------------------------
# Update Password
# ---------------------------------

@app.route("/update-password", methods=["POST"])
def update_password():

    data = json_body()

    password = data.get("password")
    email = session.get("email")

    if not password:
        return error_response("Password is required.")

    if len(password) < 6:
        return error_response("Password must be at least 6 characters.")

    if not email or not session.get("otp_verified"):
        return error_response("Verify the OTP before resetting your password.", 403)

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

    except Exception:
        app.logger.exception("Password update failed")
        return error_response("Database service is unavailable. Check MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DB in .env.", 503)


# ---------------------------------
# Run Flask
# ---------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)