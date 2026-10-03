from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb
from functools import wraps
app = Flask(__name__)
app.secret_key = "smart-digital-village-secret-key"
# MySQL Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "digital_village_service_portal"
app.config["MYSQL_PORT"] = 3306

mysql = MySQL(app)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/citizen")
def citizen():
    return render_template("citizen.html")


@app.route("/complaints")
def complaints():
    return render_template("complaints.html")


# =========================
# Government Schemes
# =========================

@app.route("/government")
def government():

    cursor = mysql.connection.cursor(
        MySQLdb.cursors.DictCursor
    )

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
    scheme = request.args.get("scheme")

    return render_template(
        "schemes/scheme_details.html",
        scheme=scheme
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
# Other Modules
# =========================

@app.route("/agriculture")
def agriculture():
    return render_template("agriculture.html")


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

@app.route("/admin/schemes/add", methods=["POST"])
@admin_required
def add_scheme():

    scheme_name = request.form.get("scheme_name", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    eligibility = request.form.get("eligibility", "").strip()
    required_documents = request.form.get(
        "required_documents", ""
    ).strip()

    last_date = request.form.get("last_date") or None

    apply_link = request.form.get(
        "apply_link", ""
    ).strip()

    status = request.form.get(
        "status",
        "Active"
    )

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
            status,
            created_by
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """, (
        scheme_name,
        category,
        description,
        eligibility,
        required_documents,
        last_date,
        apply_link,
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
# ACTIVATE / DEACTIVATE
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
# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )