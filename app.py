from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

DB_NAME = "database.db"


def init_db():
    db_exists = os.path.exists(DB_NAME)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("admin",))
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("yasmineel", "1234")
        )

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("dashboard.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    )
    user = cursor.fetchone()

    conn.close()

    if user:
        return render_template("index.html")
    else:
        return "Wrong username or password"


if __name__ == "__main__":
    init_db()
    app.run(debug=True)


