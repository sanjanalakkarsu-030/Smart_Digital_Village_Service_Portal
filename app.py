from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from datetime import date

import MySQLdb
import os

from werkzeug.utils import secure_filename
from functools import wraps


# =========================
# FLASK APP
# =========================

app = Flask(__name__)

app.secret_key = "smart-digital-village-secret-key"


# =========================
# MYSQL CONFIGURATION
# =========================

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "digital_village_service_portal"
app.config["MYSQL_PORT"] = 3306


# =========================
# MYSQL + BCRYPT
# =========================

mysql = MySQL(app)
bcrypt = Bcrypt(app)
# =========================
# HOME
# =========================


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/citizen")
def citizen():
    if "citizen_id" not in session:
        return redirect(url_for("citizen_login"))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("""
        SELECT
            citizen_id,
            full_name,
            mobile_number,
            house_number,
            ward_number,
            gender,
            address,
            username,
            registration_date,
            account_status
        FROM citizens
        WHERE citizen_id = %s
    """, (session["citizen_id"],))

    citizen_data = cursor.fetchone()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM complaints
        WHERE citizen_id = %s
    """, (session["citizen_id"],))

    complaint_count = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM agriculture_queries
        WHERE citizen_id = %s
    """, (session["citizen_id"],))

    agriculture_count = cursor.fetchone()["total"]

    cursor.close()

    if not citizen_data:
        session.clear()
        return redirect(url_for("citizen_login"))

    return render_template(
        "citizen/dashboard.html",
        citizen=citizen_data,
        complaint_count=complaint_count,
        agriculture_count=agriculture_count
    )
# =========================
# CITIZEN LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def citizen_login():

    if request.method == "GET":
        return render_template("citizen/login.html")

    data = request.get_json(silent=True) or {}

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Username and password are required."
        }), 400

    try:
        cur = mysql.connection.cursor()

        cur.execute(
    """
    SELECT
        citizen_id,
        full_name,
        username,
        password,
        account_status
    FROM citizens
    WHERE username = %s OR mobile_number = %s
    LIMIT 1
    """,
    (username, username)
)
        user = cur.fetchone()
        cur.close()

    except Exception as e:

        print("Login Error:", e)

        return jsonify({
            "success": False,
            "message": "Database error."
        }), 500

    if not user:
        return jsonify({
            "success": False,
            "message": "Invalid username or password."
        }), 401

    citizen_id = user[0]
    full_name = user[1]
    db_username = user[2]
    hashed_password = user[3]
    account_status = user[4]

    if account_status != "Active":
        return jsonify({
            "success": False,
            "message": "Your account is inactive."
        }), 403

    if bcrypt.check_password_hash(
        hashed_password,
        password
    ):

        session["citizen_id"] = citizen_id
        session["citizen_username"] = db_username
        session["citizen_name"] = full_name

        return jsonify({
            "success": True,
            "message": "Login successful!",
            "redirect": "/citizen"
        })

    return jsonify({
        "success": False,
        "message": "Invalid username or password."
    }), 401
# =========================
# CITIZEN LOGOUT
# =========================



@app.route("/citizen/logout")

def citizen_logout():
    session.pop("citizen_id", None)
    session.pop("citizen_username", None)
    session.pop("citizen_name", None)
    return redirect(url_for("home"))
# ==========================================
# FORGOT PASSWORD PAGES
# ==========================================

@app.route("/forgot-password")
def forgot_password():
    return render_template("citizen/forgot_password.html")


@app.route("/verify-otp")
def verify_otp_page():
    return render_template("citizen/verify_otp.html")


@app.route("/reset-password")
def reset_password_page():
    return render_template("citizen/reset_password.html")
# ==========================================
# ==========================================
# SEND OTP - FORGOT PASSWORD
# ==========================================

@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()

    if not username:
        return jsonify({
            "success": False,
            "message": "Please enter username or phone number."
        }), 400

    try:
        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT citizen_id, full_name
            FROM citizens
            WHERE username = %s OR mobile_number = %s
            LIMIT 1
        """, (username, username))

        user = cur.fetchone()
        cur.close()

        if not user:
            return jsonify({
                "success": False,
                "message": "No account found with this username or phone number."
            }), 404

        # Demo OTP for project testing
        otp = "123456"

        session["reset_citizen_id"] = user[0]
        session["reset_otp"] = otp

        print("PASSWORD RESET OTP:", otp)

        return jsonify({
            "success": True,
            "message": "OTP generated successfully.",
            "demo_otp": otp
        })

    except Exception as e:
        print("Send OTP Error:", e)

        return jsonify({
            "success": False,
            "message": "Database error."
        }), 500

# ==========================================
# VERIFY OTP
# ==========================================

@app.route("/verify-otp", methods=["POST"])
def verify_otp():

    data = request.get_json(silent=True) or {}

    otp = data.get("otp", "").strip()

    if not otp:
        return jsonify({
            "success": False,
            "message": "Please enter OTP."
        }), 400

    if "reset_citizen_id" not in session:
        return jsonify({
            "success": False,
            "message": "Password reset session expired."
        }), 400

    if otp != session.get("reset_otp"):
        return jsonify({
            "success": False,
            "message": "Invalid OTP."
        }), 401

    session["otp_verified"] = True

    return jsonify({
        "success": True,
        "message": "OTP verified successfully."
    })


# ==========================================
# UPDATE PASSWORD
# ==========================================

@app.route("/update-password", methods=["POST"])
def update_password():

    if "reset_citizen_id" not in session:
        return jsonify({
            "success": False,
            "message": "Password reset session expired."
        }), 400

    if not session.get("otp_verified"):
        return jsonify({
            "success": False,
            "message": "Please verify OTP first."
        }), 403

    data = request.get_json(silent=True) or {}

    password = data.get("password", "").strip()

    if not password:
        return jsonify({
            "success": False,
            "message": "Password is required."
        }), 400

    if len(password) < 6:
        return jsonify({
            "success": False,
            "message": "Password must contain at least 6 characters."
        }), 400

    try:
        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        cur = mysql.connection.cursor()

        cur.execute("""
            UPDATE citizens
            SET password = %s
            WHERE citizen_id = %s
        """, (
            hashed_password,
            session["reset_citizen_id"]
        ))

        mysql.connection.commit()
        cur.close()

        # Clear reset session
        session.pop("reset_citizen_id", None)
        session.pop("reset_otp", None)
        session.pop("otp_verified", None)

        return jsonify({
            "success": True,
            "message": "Password updated successfully."
        })

    except Exception as e:
        print("Update Password Error:", e)

        return jsonify({
            "success": False,
            "message": "Unable to update password."
        }), 500
# =========================
# CITIZEN REGISTRATION
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("citizen/register.html")

    data = request.get_json(silent=True) or {}

    full_name = data.get("full_name")
    mobile_number = data.get("mobile_number")
    house_number = data.get("house_number")
    ward_number = data.get("ward_number")
    gender = data.get("gender")
    email = data.get("email")
    address = data.get("address")
    username = data.get("username")
    password = data.get("password")

    if not all([
        full_name,
        mobile_number,
        house_number,
        ward_number,
        gender,
        email,
        address,
        username,
        password
    ]):
        return jsonify({
            "success": False,
            "message": "All fields are required."
        }), 400

    try:
        cur = mysql.connection.cursor()

        # Check username
        cur.execute(
            "SELECT citizen_id FROM citizens WHERE username = %s",
            (username,)
        )

        if cur.fetchone():
            cur.close()

            return jsonify({
                "success": False,
                "message": "Username already exists."
            }), 409

        # Check email
        cur.execute(
            "SELECT citizen_id FROM citizens WHERE email = %s",
            (email,)
        )

        if cur.fetchone():
            cur.close()

            return jsonify({
                "success": False,
                "message": "Email already registered."
            }), 409

        # Hash password
        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        # Insert citizen
        cur.execute(
            """
            INSERT INTO citizens
            (
                full_name,
                mobile_number,
                house_number,
                ward_number,
                gender,
                email,
                address,
                username,
                password,
                registration_date,
                account_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                full_name,
                mobile_number,
                house_number,
                ward_number,
                gender,
                email,
                address,
                username,
                hashed_password,
                date.today(),
                "Active"
            )
        )

        mysql.connection.commit()
        cur.close()

        return jsonify({
            "success": True,
            "message": "Registration successful!"
        }), 201

    except Exception as e:

        print("Registration Error:", e)

        return jsonify({
            "success": False,
            "message": "Registration failed."
        }), 500

# =========================
# complaint module
# =========================

@app.route("/complaints")
def complaints():
    if "citizen_id" not in session:
        return redirect(url_for("citizen_login"))

    return render_template("complaint/comp_reg.html")
    

@app.route("/complaints/submit", methods=["POST"])
def submit_complaint():
    if "citizen_id" not in session:
        return jsonify({"success": False, "message": "Please login first"}), 401

    data = request.get_json(silent=True) or {}

    category = (data.get("category") or "").strip()
    subject = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    location = (data.get("location") or "").strip()

    if not all([category, subject, description, location]):
        return jsonify({
            "success": False,
            "message": "Please fill all required fields."
        }), 400

    cur = None
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT ward_number FROM citizens WHERE citizen_id = %s",
            (session["citizen_id"],)
        )
        citizen = cur.fetchone()

        if not citizen or not citizen[0]:
            return jsonify({
                "success": False,
                "message": "Please add your ward number to your profile."
            }), 400

        cur.execute("""
            INSERT INTO complaints
                (citizen_id, ward_number, category, subject,
                 description, location, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
        """, (
            session["citizen_id"], citizen[0], category,
            subject, description, location
        ))

        mysql.connection.commit()
        new_id = cur.lastrowid

        return jsonify({
            "success": True,
            "message": "Complaint saved successfully.",
            "complaint_id": new_id
        }), 201

    except Exception:
        mysql.connection.rollback()
        app.logger.exception("Complaint save failed")
        return jsonify({
            "success": False,
            "message": "Database save failed. Check the Flask terminal."
        }), 500

    finally:
        if cur:
            cur.close()


@app.route("/api/my-complaints", methods=["GET"])
def get_my_complaints():
    if "citizen_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first"
        }), 401

    cur = None
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT complaint_id, category, subject, description,
                   location, complaint_date, status, admin_remarks
            FROM complaints
            WHERE citizen_id = %s
            ORDER BY complaint_id DESC
        """, (session["citizen_id"],))

        rows = cur.fetchall()
        complaints = []

        for row in rows:
            complaints.append({
                "id": row[0],
                "category": row[1],
                "title": row[2],
                "description": row[3],
                "location": row[4],
                "date": row[5].strftime("%d %b %Y, %I:%M %p")
                       if row[5] else "",
                "status": row[6],
                "admin_remarks": row[7] or ""
            })

        return jsonify({
            "success": True,
            "complaints": complaints
        })

    except Exception:
        app.logger.exception("Could not fetch citizen complaints")
        return jsonify({
            "success": False,
            "message": "Could not load complaints"
        }), 500

    finally:
        if cur:
            cur.close()
# =========================
# Government Schemes
# =========================

@app.route("/government")
def government():

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("""
        SELECT
            scheme_id,
            scheme_name,
            category,
            description,
            eligibility,
            required_documents,
            last_date,
            apply_link,
            image_path,
            status
        FROM government_schemes
        WHERE status = 'Active'
        ORDER BY scheme_id DESC
    """)

    schemes = cursor.fetchall()

    cursor.close()

    return render_template(
        "schemes/schemes.html",
        schemes=schemes
    )    

@app.route("/government/details")
def scheme_details():

    scheme_id = request.args.get("scheme")

    # If it is a numeric ID, get the scheme from MySQL
    if scheme_id and scheme_id.isdigit():

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("""
            SELECT scheme_id, scheme_name, category, description,
                   eligibility, required_documents, last_date,
                   apply_link, status
            FROM government_schemes
            WHERE scheme_id = %s
              AND status = 'Active'
        """, (scheme_id,))

        db_scheme = cursor.fetchone()
        cursor.close()

        if db_scheme:
            return render_template(
                "schemes/scheme_details.html",
                db_scheme=db_scheme
            )

    # Existing 16 schemes continue exactly as before
    return render_template(
        "schemes/scheme_details.html",
        scheme=scheme_id
    )
@app.route("/government/apply")
def apply_scheme():
    scheme = request.args.get("scheme")

    return render_template(
        "schemes/apply_scheme.html",
        scheme=scheme
    )


# =========================
# Village Announcements
# =========================

# =========================
# Village Announcements
# =========================

@app.route("/announcements")
def announcements():

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("""
        SELECT
            a.announcement_id,
            a.title,
            a.description,
            a.category,
            a.event_date,
            a.posted_by,
            a.published_date,
            a.status,
            ad.full_name AS posted_by_name
        FROM announcements a
        JOIN admins ad
            ON a.posted_by = ad.admin_id
        WHERE a.status = 'Published'
        ORDER BY a.published_date DESC
    """)

    announcements = cursor.fetchall()

    # Get admins for Add Announcement form
    cursor.execute("""
        SELECT admin_id, full_name
        FROM admins
        ORDER BY full_name
    """)

    admins = cursor.fetchall()

    cursor.close()

    return render_template(
        "announcements/announcements.html",
        announcements=announcements,
        admins=admins
    )


# =========================
# Add Announcement
# =========================

@app.route("/announcements/add", methods=["POST"])
def add_announcement():

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "Panchayat")
    event_date = request.form.get("event_date") or None
    posted_by = request.form.get("posted_by")
    status = request.form.get("status", "Published")

    if not title or not description or not posted_by:
        return "Please fill all required fields.", 400

    cursor = mysql.connection.cursor()

    cursor.execute("""
        INSERT INTO announcements
        (
            title,
            description,
            category,
            event_date,
            posted_by,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        title,
        description,
        category,
        event_date,
        posted_by,
        status
    ))

    mysql.connection.commit()
    cursor.close()

    return redirect (url_for("announcements"))


# =========================
# Announcement Details
# =========================

@app.route("/announcements/details/<int:announcement_id>")
def announcement_details(announcement_id):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("""
        SELECT
            a.announcement_id,
            a.title,
            a.description,
            a.category,
            a.event_date,
            a.posted_by,
            a.published_date,
            a.status,
            ad.full_name AS posted_by_name
        FROM announcements a
        JOIN admins ad
            ON a.posted_by = ad.admin_id
        WHERE a.announcement_id = %s
        AND a.status = 'Published'
    """, (announcement_id,))

    announcement = cursor.fetchone()
    cursor.close()

    if not announcement:
        return "Announcement not found", 404

    return render_template(
        "announcements/announcements_details.html",
        announcement=announcement
    )
# =========================
# Agriculture Module
# =========================

@app.route("/agriculture")
def agriculture():
    return render_template("AgricultureSupport/index.html")


@app.route("/agriculture/crops")
def crop_details():
    return render_template("AgricultureSupport/crop-details.html")


@app.route("/agriculture/fertilizer")
def agriculture_fertilizer():
    return render_template("AgricultureSupport/fertilizer.html")


@app.route("/agriculture/weather")
def agriculture_weather():
    return render_template("AgricultureSupport/weather.html")


@app.route("/agriculture/query")
def agriculture_query():

    if "citizen_id" not in session:
        return redirect(url_for("citizen_login"))

    return render_template("AgricultureSupport/farmer-query.html")


@app.route("/agriculture/disease")
def agriculture_disease():
    return render_template("AgricultureSupport/disease-prediction.html")


@app.route("/agriculture/cost")
def agriculture_cost():
    return render_template("AgricultureSupport/farming-cost.html")


@app.route("/agriculture/tips")
def agriculture_tips():
    return render_template("AgricultureSupport/farming-tips.html")


@app.route("/agriculture/records")
def agriculture_records():
    return render_template("AgricultureSupport/farm-records.html")


# =========================
# Agriculture Query Submit
# =========================

@app.route("/agriculture/query/submit", methods=["POST"])
def submit_agriculture_query():

    if "citizen_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "Invalid request."
            }), 400

        crop_name = data.get("crop_name", "").strip()
        soil_type = data.get("soil_type", "").strip()
        farmer_query = data.get("farmer_query", "").strip()

        if not crop_name:
            return jsonify({
                "success": False,
                "message": "Please enter crop name."
            }), 400

        if not farmer_query:
            return jsonify({
                "success": False,
                "message": "Please enter your question."
            }), 400

        cursor = mysql.connection.cursor()

        cursor.execute("""
            INSERT INTO agriculture_queries
            (
                citizen_id,
                crop_name,
                soil_type,
                farmer_query,
                status
            )
            VALUES (%s, %s, %s, %s, 'Pending')
        """, (
            session["citizen_id"],
            crop_name,
            soil_type,
            farmer_query
        ))

        mysql.connection.commit()

        cursor.close()

        return jsonify({
            "success": True,
            "message": "Agriculture query submitted successfully."
        })

    except Exception as e:

        print("Agriculture Query Error:", e)

        return jsonify({
            "success": False,
            "message": "Failed to submit agriculture query."
        }), 500
     # =========================
    # agriculture new Module
    # =========================
     
@app.route("/agriculture/new")
def agriculture_new():
    return render_template("agriculture_new/index.html")









@app.route("/agriculture/new/crops", methods=["GET", "POST"])
def agriculture_crops_new():
    form_data = {
        "district": "",
        "mandal": "",
        "village": "",
        "season": "Unknown",
        "soil_type": "Unknown",
        "water": "Unknown",
        "soil_test": "No"
    }

    recommendations = None
    error_message = None
    pending_count = 0

    if request.method == "POST":
        for key in form_data:
            form_data[key] = request.form.get(
                key, form_data[key]
            ).strip()

        # Accept only the values provided by the form.
        allowed_values = {
            "season": {"Kharif", "Rabi", "Summer", "Unknown"},
            "soil_type": {
                "Black", "Red", "Sandy", "Loamy", "Unknown"
            },
            "water": {"Low", "Medium", "High", "Unknown"},
            "soil_test": {"Yes", "No"}
        }

        invalid = any(
            form_data[key] not in allowed
            for key, allowed in allowed_values.items()
        )

        if invalid:
            recommendations = []
            error_message = "Please select valid form options."
        else:
            cursor = None

            try:
                cursor = mysql.connection.cursor()

                # Match only location details the farmer supplied.
                location_conditions = []
                location_params = []

                for field, column in [
                    ("district", "district_name"),
                    ("mandal", "mandal_name"),
                    ("village", "village_name")
                ]:
                    value = form_data[field].strip()

                    if value:
                        value = value.lower()
                        for suffix in (" district", " mandal", " village"):
                            if value.endswith(suffix):
                                value = value[:-len(suffix)].strip()

                        location_conditions.append(
                            f"LOWER(TRIM(COALESCE(l.{column}, ''))) = %s"
                        )
                        location_params.append(value)

                sql = """
                    SELECT
                        c.crop_name,
                        cr.season,
                        cr.soil_type,
                        cr.water_requirement,
                        cr.guidance,
                        s.source_url,
                        s.source_name,
                        cr.verified_date,
                        cr.verification_status,
                        cr.sowing_months,
                        s.verification_status
                    FROM crops c
                    INNER JOIN crop_requirements cr
                        ON cr.crop_id = c.crop_id
                    LEFT JOIN agriculture_sources s
                        ON s.source_id = cr.source_id
                    WHERE c.is_active = 1
                """

                if location_conditions:
                    sql += """
                        AND EXISTS (
                            SELECT 1
                            FROM locations l
                            WHERE l.location_id = cr.location_id
                              AND l.is_active = 1
                              AND l.location_level = 'Village'
                              AND
                    """
                    sql += " AND ".join(location_conditions)
                    sql += ")"

                sql += " ORDER BY c.crop_name"

                cursor.execute(sql, tuple(location_params))
                rows = cursor.fetchall()

                # Pending records are never treated as recommendations.
                pending_count = sum(
                    1 for row in rows if row[8] == "Pending"
                )

                recommendations = []

                season = form_data["season"].lower()
                soil_type = form_data["soil_type"].lower()
                water = form_data["water"].lower()

                for row in rows:
                    (
                        name, crop_season, soil, crop_water,
                        guidance, url, source, verified_date,
                        crop_status, sowing_months, source_status
                    ) = row

                    if crop_status != "Verified":
                        continue

                    if source_status != "Verified" or not url:
                        continue

                    # A selected condition must have matching
                    # verified information; missing data is not a match.
                    if season != "unknown":
                        if not crop_season or season not in crop_season.lower():
                            continue

                    if soil_type != "unknown":
                        if not soil or soil_type not in soil.lower():
                            continue

                    if water != "unknown":
                        if not crop_water or water not in crop_water.lower():
                            continue

                    recommendations.append((
                        name, crop_season, soil, crop_water,
                        guidance, url, source, verified_date,
                        crop_status, sowing_months
                    ))

            except Exception:
                app.logger.exception("Crop guidance query failed")
                recommendations = None
                error_message = (
                    "Unable to load crop guidance. "
                    "Check the Flask terminal and database connection."
                )

            finally:
                if cursor is not None:
                    cursor.close()

    return render_template(
        "agriculture_new/crops.html",
        form_data=form_data,
        recommendations=recommendations,
        error_message=error_message,
        pending_count=pending_count
    )
@app.route("/agriculture/new/soil")
def agriculture_soil_new():
    return render_template(
        "agriculture_new/soil_health.html"
    )


@app.route("/agriculture/new/weather")
def agriculture_weather_new():
    return (
        "Weather and Rainfall Information page "
        "is coming soon."
    )


@app.route("/agriculture/new/market")
def agriculture_market_new():
    return (
        "Agricultural Market Prices page "
        "is coming soon."
    )




    # =========================
# health Module
# =========================
@app.route("/health")
def health():
    return render_template("health.html")
# -----------------------------
    # admin module
    # -----------------------------
    # ============================================================
# ADMIN AUTHENTICATION
# ============================================================

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "admin_id" not in session:
            return redirect(url_for("admin_login"))

        return f(*args, **kwargs)

    return decorated_function


# ============================================================
# ADMIN LOGIN
# ============================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    # Already logged in
    if "admin_id" in session:
        return redirect(url_for("admin"))

    error = None

    if request.method == "POST":

        login_id = request.form.get("login_id", "").strip()
        password = request.form.get("password", "").strip()

        cursor = mysql.connection.cursor(
            MySQLdb.cursors.DictCursor
        )

        cursor.execute("""
            SELECT
                admin_id,
                full_name,
                username,
                password,
                email,
                mobile,
                role
            FROM admins
            WHERE username = %s
               OR email = %s
               OR mobile = %s
        """, (login_id, login_id, login_id))

        admin_user = cursor.fetchone()

        cursor.close()

        # Validate admin credentials
        if admin_user and admin_user["password"] == password:

            session["admin_id"] = admin_user["admin_id"]
            session["admin_name"] = admin_user["full_name"]
            session["admin_role"] = admin_user["role"]

            return redirect(url_for("admin"))

        error = "Invalid username, email/mobile number, or password."

    return render_template(
        "admin/login.html",
        error=error
    )

#
# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(url_for("home"))

# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin")
@admin_required
def admin():

    cursor = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    # --------------------------------------------------------
    # Dashboard Statistics
    # --------------------------------------------------------

    # Total Citizens
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM citizens
    """)

    total_citizens = cursor.fetchone()["total"]


    # Total Complaints
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM complaints
    """)

    total_complaints = cursor.fetchone()["total"]


    # Resolved Complaints
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM complaints
        WHERE status = 'Resolved'
    """)

    resolved_complaints = cursor.fetchone()["total"]


    # Pending Complaints
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM complaints
        WHERE status = 'Pending'
    """)

    pending_complaints = cursor.fetchone()["total"]


    # In Progress Complaints
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM complaints
        WHERE status = 'In Progress'
    """)

    in_progress_complaints = cursor.fetchone()["total"]


    # Active Government Schemes
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM government_schemes
        WHERE status = 'Active'
    """)

    total_schemes = cursor.fetchone()["total"]


    # Published Announcements
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM announcements
        WHERE status = 'Published'
    """)

    total_announcements = cursor.fetchone()["total"]


    # Agriculture Information
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM agriculture_information
    """)

    agriculture_posts = cursor.fetchone()["total"]


    # Health Information
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM health_information
    """)

    health_updates = cursor.fetchone()["total"]


    # --------------------------------------------------------
    # Recent Complaints
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            c.complaint_id,
            c.category,
            c.subject,
            c.status,
            ci.full_name
        FROM complaints c
        JOIN citizens ci
            ON c.citizen_id = ci.citizen_id
        ORDER BY c.complaint_id DESC
        LIMIT 5
    """)

    recent_complaints = cursor.fetchall()


    # --------------------------------------------------------
    # Recent Announcements
    # --------------------------------------------------------

    cursor.execute("""
        SELECT
            announcement_id,
            title,
            description,
            event_date,
            published_date
        FROM announcements
        WHERE status = 'Published'
        ORDER BY published_date DESC
        LIMIT 3
    """)

    recent_announcements = cursor.fetchall()


    # Close database cursor
    cursor.close()


    # --------------------------------------------------------
    # Send Data To Dashboard
    # --------------------------------------------------------

    return render_template(
        "admin/dashboard.html",

        total_citizens=total_citizens,

        total_complaints=total_complaints,

        resolved_complaints=resolved_complaints,

        pending_complaints=pending_complaints,

        in_progress_complaints=in_progress_complaints,

        total_schemes=total_schemes,

        total_announcements=total_announcements,

        agriculture_posts=agriculture_posts,

        health_updates=health_updates,

        recent_complaints=recent_complaints,

        recent_announcements=recent_announcements
    )


# ============================================================
# MANAGE CITIZENS
# ============================================================

@app.route("/admin/citizens")
@admin_required
def manage_citizens():

    cursor = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cursor.execute("""
        SELECT
            citizen_id,
            full_name,
            mobile_number,
            house_number,
            ward_number,
            gender,
            address,
            username,
            registration_date,
            account_status
        FROM citizens
        ORDER BY citizen_id DESC
    """)

    citizens = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin/citizens.html",
        citizens=citizens
    )


# ============================================================
# VIEW CITIZEN
# ============================================================

@app.route("/admin/citizens/view/<int:citizen_id>")
@admin_required
def view_citizen(citizen_id):

    cursor = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cursor.execute("""
        SELECT *
        FROM citizens
        WHERE citizen_id = %s
    """, (citizen_id,))

    citizen = cursor.fetchone()

    cursor.close()

    if not citizen:
        return "Citizen not found", 404

    return render_template(
        "admin/citizen_view.html",
        citizen=citizen
    )


# ============================================================
# DELETE CITIZEN
# ============================================================

@app.route("/admin/citizens/delete/<int:citizen_id>")
@admin_required
def delete_citizen(citizen_id):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM citizens
        WHERE citizen_id = %s
    """, (citizen_id,))

    mysql.connection.commit()

    cursor.close()

    return redirect(
        url_for("manage_citizens")
    )
# ============================================================
# ADMIN - MANAGE COMPLAINTS
# ============================================================


# ------------------------------------------------------------
# View All Complaints
# ------------------------------------------------------------

@app.route("/admin/complaints")
@admin_required
def manage_complaints():

    cursor = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cursor.execute("""
        SELECT
            c.complaint_id,
            c.citizen_id,
            c.ward_number,
            c.category,
            c.subject,
            c.description,
            c.location,
            c.image_path,
            c.complaint_date,
            c.status,
            c.admin_remarks,
            c.resolved_date,
            ci.full_name,
            ci.mobile_number
        FROM complaints c
        JOIN citizens ci
            ON c.citizen_id = ci.citizen_id
        ORDER BY c.complaint_id DESC
    """)

    complaints = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin/complaints.html",
        complaints=complaints
    )


# ------------------------------------------------------------
# View Complaint Details
# ------------------------------------------------------------

@app.route("/admin/complaints/view/<int:complaint_id>")
@admin_required
def view_complaint(complaint_id):

    cursor = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cursor.execute("""
        SELECT
            c.complaint_id,
            c.citizen_id,
            c.ward_number,
            c.category,
            c.subject,
            c.description,
            c.location,
            c.image_path,
            c.complaint_date,
            c.status,
            c.admin_remarks,
            c.resolved_date,

            ci.full_name,
            ci.mobile_number,
            ci.house_number,
            ci.address,
            ci.gender

        FROM complaints c

        JOIN citizens ci
            ON c.citizen_id = ci.citizen_id

        WHERE c.complaint_id = %s
    """, (complaint_id,))

    complaint = cursor.fetchone()

    cursor.close()

    if not complaint:
        return "Complaint not found", 404

    return render_template(
        "admin/complaint_view.html",
        complaint=complaint
    )


# ------------------------------------------------------------
# Update Complaint Status + Admin Remarks
# ------------------------------------------------------------

@app.route(
    "/admin/complaints/update/<int:complaint_id>",
    methods=["POST"]
)
@admin_required
def update_complaint(complaint_id):

    status = request.form.get("status")
    admin_remarks = request.form.get(
        "admin_remarks",
        ""
    ).strip()

    allowed_statuses = [
        "Pending",
        "In Progress",
        "Resolved"
    ]

    if status not in allowed_statuses:

        return "Invalid complaint status", 400


    cursor = mysql.connection.cursor()


    # If complaint is resolved
    if status == "Resolved":

        cursor.execute("""
            UPDATE complaints

            SET
                status = %s,
                admin_remarks = %s,
                resolved_date = CURDATE()

            WHERE complaint_id = %s
        """, (
            status,
            admin_remarks,
            complaint_id
        ))


    # If complaint is not resolved
    else:

        cursor.execute("""
            UPDATE complaints

            SET
                status = %s,
                admin_remarks = %s,
                resolved_date = NULL

            WHERE complaint_id = %s
        """, (
            status,
            admin_remarks,
            complaint_id
        ))


    mysql.connection.commit()

    cursor.close()


    return redirect(
        url_for(
            "view_complaint",
            complaint_id=complaint_id
        )
    )


# ------------------------------------------------------------
# Delete Complaint
# ------------------------------------------------------------

@app.route(
    "/admin/complaints/delete/<int:complaint_id>",
    methods=["POST"]
)
@admin_required
def delete_complaint(complaint_id):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM complaints
        WHERE complaint_id = %s
    """, (complaint_id,))

    mysql.connection.commit()

    cursor.close()

    return redirect(
        url_for("manage_complaints")
    )
# ==========================================================
# ADMIN - GOVERNMENT SCHEMES
# ==========================================================

@app.route("/admin/schemes")
@admin_required
def manage_schemes():

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("""
        SELECT
            gs.scheme_id,
            gs.scheme_name,
            gs.category,
            gs.description,
            gs.eligibility,
            gs.required_documents,
            gs.last_date,
            gs.apply_link,
            gs.status,
            gs.created_at,
            gs.created_by,
            a.full_name AS created_by_name
        FROM government_schemes gs
        LEFT JOIN admins a
            ON gs.created_by = a.admin_id
        ORDER BY gs.scheme_id DESC
    """)

    schemes = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin/schemes.html",
        schemes=schemes
    )


# ==========================================================
# ADD NEW SCHEME
# ==========================================================

# ==========================================================
# ADD SCHEME
# ==========================================================

@app.route("/admin/schemes/add", methods=["POST"])
@admin_required
def add_scheme():

    scheme_name = request.form.get("scheme_name", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    eligibility = request.form.get("eligibility", "").strip()
    required_documents = request.form.get("required_documents", "").strip()
    last_date = request.form.get("last_date") or None
    apply_link = request.form.get("apply_link", "").strip()
    status = request.form.get("status", "Active")

    created_by = session.get("admin_id")

    if not scheme_name:
        return "Scheme name is required.", 400

    if not category:
        return "Category is required.", 400

    if not description:
        return "Description is required.", 400

    if not eligibility:
        return "Eligibility is required.", 400

    if not required_documents:
        return "Required documents are required.", 400

    if not created_by:
        return redirect(url_for("admin_login"))

    # -----------------------------
    # SAVE IMAGE
    # -----------------------------

    image = request.files.get("image")
    image_path = None

    if image and image.filename:

        filename = secure_filename(image.filename)

        upload_folder = os.path.join(
            app.root_path,
            "static",
            "images",
            "schemes"
        )

        os.makedirs(upload_folder, exist_ok=True)

        image.save(
            os.path.join(upload_folder, filename)
        )

        image_path = filename

    # -----------------------------
    # INSERT INTO DATABASE
    # -----------------------------

    cursor = mysql.connection.cursor()

    cursor.execute("""
        INSERT INTO government_schemes
        (
            scheme_name,
            category,
            description,
            eligibility,
            required_documents,
            last_date,
            apply_link,
            image_path,
            status,
            created_by
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        scheme_name,
        category,
        description,
        eligibility,
        required_documents,
        last_date,
        apply_link,
        image_path,
        status,
        created_by
    ))

    mysql.connection.commit()
    cursor.close()

    return redirect(url_for("manage_schemes"))


# ==========================================================
# VIEW SCHEME
# ==========================================================

@app.route("/admin/schemes/view/<int:scheme_id>")
@admin_required
def view_scheme(scheme_id):

    cursor = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cursor.execute("""
        SELECT
            gs.*,
            a.full_name AS created_by_name
        FROM government_schemes gs
        LEFT JOIN admins a
            ON gs.created_by = a.admin_id
        WHERE gs.scheme_id = %s
    """, (scheme_id,))

    scheme = cursor.fetchone()

    cursor.close()

    if not scheme:
        return "Government scheme not found.", 404

    return render_template(
        "admin/scheme_view.html",
        scheme=scheme
    )


# ==========================================================
# EDIT SCHEME
# ==========================================================

@app.route(
    "/admin/schemes/edit/<int:scheme_id>",
    methods=["GET", "POST"]
)
@admin_required
def edit_scheme(scheme_id):

    cursor = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    # -----------------------------
    # UPDATE SCHEME
    # -----------------------------

    if request.method == "POST":

        scheme_name = request.form.get(
            "scheme_name", ""
        ).strip()

        category = request.form.get(
            "category", ""
        ).strip()

        description = request.form.get(
            "description", ""
        ).strip()

        eligibility = request.form.get(
            "eligibility", ""
        ).strip()

        required_documents = request.form.get(
            "required_documents", ""
        ).strip()

        last_date = request.form.get(
            "last_date"
        ) or None

        apply_link = request.form.get(
            "apply_link", ""
        ).strip()

        status = request.form.get(
            "status",
            "Active"
        )

        # -----------------------------
        # GET NEW IMAGE
        # -----------------------------

        image = request.files.get("image")

        image_path = None

        if image and image.filename:

            filename = secure_filename(
                image.filename
            )

            upload_folder = os.path.join(
                app.root_path,
                "static",
                "images",
                "schemes"
            )

            os.makedirs(
                upload_folder,
                exist_ok=True
            )

            image.save(
                os.path.join(
                    upload_folder,
                    filename
                )
            )

            image_path = filename

        # -----------------------------
        # UPDATE WITH IMAGE
        # -----------------------------

        if image_path:

            cursor.execute("""
                UPDATE government_schemes
                SET
                    scheme_name = %s,
                    category = %s,
                    description = %s,
                    eligibility = %s,
                    required_documents = %s,
                    last_date = %s,
                    apply_link = %s,
                    image_path = %s,
                    status = %s
                WHERE scheme_id = %s
            """, (
                scheme_name,
                category,
                description,
                eligibility,
                required_documents,
                last_date,
                apply_link,
                image_path,
                status,
                scheme_id
            ))

        else:

            cursor.execute("""
                UPDATE government_schemes
                SET
                    scheme_name = %s,
                    category = %s,
                    description = %s,
                    eligibility = %s,
                    required_documents = %s,
                    last_date = %s,
                    apply_link = %s,
                    status = %s
                WHERE scheme_id = %s
            """, (
                scheme_name,
                category,
                description,
                eligibility,
                required_documents,
                last_date,
                apply_link,
                status,
                scheme_id
            ))

        mysql.connection.commit()

        cursor.close()

        return redirect(
            url_for("manage_schemes")
        )

    # -----------------------------
    # GET EXISTING SCHEME
    # -----------------------------

    cursor.execute("""
        SELECT *
        FROM government_schemes
        WHERE scheme_id = %s
    """, (scheme_id,))

    scheme = cursor.fetchone()

    cursor.close()

    if not scheme:
        return "Government scheme not found.", 404

    return render_template(
        "admin/scheme_edit.html",
        scheme=scheme
    )


# ==========================================================
# ACTIVATE / DEACTIVATE SCHEME
# ==========================================================

@app.route(
    "/admin/schemes/toggle/<int:scheme_id>",
    methods=["POST"]
)
@admin_required
def toggle_scheme(scheme_id):

    cursor = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

    cursor.execute("""
        SELECT status
        FROM government_schemes
        WHERE scheme_id = %s
    """, (scheme_id,))

    scheme = cursor.fetchone()

    if not scheme:
        cursor.close()
        return "Government scheme not found.", 404

    if scheme["status"] == "Active":
        new_status = "Inactive"
    else:
        new_status = "Active"

    cursor.execute("""
        UPDATE government_schemes
        SET status = %s
        WHERE scheme_id = %s
    """, (
        new_status,
        scheme_id
    ))

    mysql.connection.commit()
    cursor.close()

    return redirect(
        url_for("manage_schemes")
    )


# ==========================================================
# DELETE SCHEME
# ==========================================================

@app.route(
    "/admin/schemes/delete/<int:scheme_id>",
    methods=["POST"]
)
@admin_required
def delete_scheme(scheme_id):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        DELETE FROM government_schemes
        WHERE scheme_id = %s
    """, (scheme_id,))

    mysql.connection.commit()
    cursor.close()

    return redirect(
        url_for("manage_schemes")

    )

@app.route("/admin/crop-verification")
@admin_required
def admin_crop_verification():

    cursor = None

    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute("""
            SELECT
                cr.requirement_id,
                cr.crop_id,
                c.crop_name,
                cr.season,
                cr.sowing_months,
                cr.soil_type,
                cr.water_requirement,
                cr.rainfall_requirement,
                cr.temperature_requirement,
                cr.soil_ph_min,
                cr.soil_ph_max,
                cr.guidance,
                cr.verification_status,
                cr.review_notes,
                s.source_name,
                s.source_url,
                s.verification_status AS source_status
            FROM crop_requirements cr
            INNER JOIN crops c
                ON c.crop_id = cr.crop_id
            LEFT JOIN agriculture_sources s
                ON s.source_id = cr.source_id
            WHERE cr.verification_status = 'Pending'
            ORDER BY cr.created_at DESC
        """)

        pending_crops = cursor.fetchall()

        return render_template(
            "admin/crop_verification.html",
            pending_crops=pending_crops,
            pending_count=len(pending_crops)
        )

    except Exception:
        app.logger.exception(
            "Failed to load crop verification page"
        )
        return (
            "Unable to load Crop Verification. "
            "Check the Flask terminal for the database error.",
            500
        )

    finally:
        if cursor is not None:
            cursor.close()

@app.route(
    "/admin/crop-verification/<int:requirement_id>/action",
    methods=["POST"]
)
@admin_required
def admin_crop_verification_action(requirement_id):

    action = request.form.get("action", "").strip().lower()
    review_notes = request.form.get("review_notes", "").strip()

    if action not in ("verify", "reject"):
        return "Invalid verification action.", 400

    new_status = "Verified" if action == "verify" else "Inactive"

    cursor = None

    try:
        cursor = mysql.connection.cursor()

        cursor.execute("""
            SELECT verification_status
            FROM crop_requirements
            WHERE requirement_id = %s
        """, (requirement_id,))

        existing = cursor.fetchone()

        if not existing:
            return "Crop requirement not found.", 404

        if existing[0] != "Pending":
            return "This crop requirement has already been reviewed.", 400

        if action == "verify" and not review_notes:
            return (
                "Please enter verification notes before approving.",
                400
            )

        cursor.execute("""
            UPDATE crop_requirements
            SET
                verification_status = %s,
                review_notes = %s,
                verified_date = CASE
                    WHEN %s = 'Verified' THEN CURDATE()
                    ELSE NULL
                END
            WHERE requirement_id = %s
              AND verification_status = 'Pending'
        """, (
            new_status,
            review_notes or None,
            new_status,
            requirement_id
        ))

        mysql.connection.commit()

        from flask import flash
        flash(
            "Crop requirement verified successfully."
            if action == "verify"
            else "Crop requirement marked inactive.",
            "success"
        )

        return redirect(url_for("admin_crop_verification"))

    except Exception:
        mysql.connection.rollback()
        app.logger.exception(
            "Crop verification action failed"
        )
        return (
            "Unable to save the review. Check the Flask terminal.",
            500
        )

    finally:
        if cursor is not None:
            cursor.close()
# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )