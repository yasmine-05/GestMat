from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "gestmat-secret-key"

DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            reference TEXT NOT NULL,
            marque TEXT NOT NULL,
            date_achat TEXT NOT NULL,
            quantite INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material_id INTEGER,
            type_maintenance TEXT NOT NULL,
            date_maintenance TEXT NOT NULL,
            statut TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (material_id) REFERENCES materials(id)
        )
    """)

    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE username = ?",
        ("yasmineel",)
    )

    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("yasmineel", "1234")
        )

    conn.commit()
    conn.close()

@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, username
        FROM users
        WHERE username = ? AND password = ?
        """,
        (username, password)
    )

    user = cursor.fetchone()

    conn.close()

    if user:

        session["user_id"] = user[0]
        session["username"] = user[1]

        return redirect(url_for("home"))

    else:
        return """
        <h2>Identifiant ou mot de passe incorrect.</h2>
        <a href="/">Retour à la connexion</a>
        """

@app.route("/dashboard")
def home():

    if "user_id" not in session:
        return redirect(url_for("login_page"))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM materials"
    )
    total_materials = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COALESCE(SUM(quantite), 0) FROM materials"
    )
    total_quantity = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM maintenance"
    )
    total_maintenance = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM maintenance
        WHERE statut = 'En maintenance'
    """)
    materials_in_maintenance = cursor.fetchone()[0]

    cursor.execute("""
        SELECT *
        FROM materials
        ORDER BY id DESC
        LIMIT 6
    """)
    recent_materials = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_materials=total_materials,
        total_quantity=total_quantity,
        total_maintenance=total_maintenance,
        materials_in_maintenance=materials_in_maintenance,
        recent_materials=recent_materials
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login_page"))

@app.route("/materials")
def materials():

    if "user_id" not in session:
        return redirect(url_for("login_page"))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM materials
        ORDER BY id DESC
    """)

    materials = cursor.fetchall()

    conn.close()

    return render_template(
        "materials.html",
        materials=materials
    )

@app.route("/add-material", methods=["GET", "POST"])
def add_material():

    if "user_id" not in session:
        return redirect(url_for("login_page"))

    if request.method == "POST":

        material_type = request.form.get("type")
        reference = request.form.get("reference")
        marque = request.form.get("marque")
        date_achat = request.form.get("date_achat")
        quantite = request.form.get("quantite")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO materials
            (
                type,
                reference,
                marque,
                date_achat,
                quantite
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            material_type,
            reference,
            marque,
            date_achat,
            quantite
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("materials"))

    return render_template("add_material.html")

@app.route("/maintenance")
def maintenance():

    if "user_id" not in session:
        return redirect(url_for("login_page"))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            maintenance.id,
            materials.type,
            materials.reference,
            maintenance.type_maintenance,
            maintenance.date_maintenance,
            maintenance.statut,
            maintenance.description
        FROM maintenance
        LEFT JOIN materials
        ON maintenance.material_id = materials.id
        ORDER BY maintenance.id DESC
    """)

    maintenances = cursor.fetchall()

    conn.close()

    return render_template(
        "maintenance.html",
        maintenances=maintenances
    )

@app.route("/add-maintenance", methods=["GET", "POST"])
def add_maintenance():

    if "user_id" not in session:
        return redirect(url_for("login_page"))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if request.method == "POST":

        material_id = request.form.get("material_id")
        type_maintenance = request.form.get("type_maintenance")
        date_maintenance = request.form.get("date_maintenance")
        statut = request.form.get("statut")
        description = request.form.get("description")

        cursor.execute("""
            INSERT INTO maintenance
            (
                material_id,
                type_maintenance,
                date_maintenance,
                statut,
                description
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            material_id,
            type_maintenance,
            date_maintenance,
            statut,
            description
        ))

        conn.commit()
        conn.close()

        return redirect(url_for("maintenance"))

    cursor.execute("""
        SELECT
            id,
            type,
            reference,
            marque
        FROM materials
        ORDER BY id DESC
    """)

    materials = cursor.fetchall()

    conn.close()

    return render_template(
        "add_maintenance.html",
        materials=materials
    )

@app.route("/users")
def users():

    if "user_id" not in session:
        return redirect(url_for("login_page"))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username
        FROM users
        ORDER BY id ASC
    """)

    users = cursor.fetchall()

    conn.close()

    return render_template(
        "users.html",
        users=users
    )

@app.route("/delete-user/<int:user_id>")
def delete_user(user_id):

    if "user_id" not in session:
        return redirect(url_for("login_page"))

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM users WHERE id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("users"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)


