from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import MySQLdb
app = Flask(__name__)
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

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT scheme_id,
               scheme_name,
               category,
               description,
               eligibility,
               required_documents,
               last_date,
               apply_link
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

    return redirect(url_for("announcements"))


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


@app.route("/admin")
def admin():
    return render_template("admin.html")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )