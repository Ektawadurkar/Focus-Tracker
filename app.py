
from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------- DATABASE ---------------- #

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create users table if not exists
def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            duration INTEGER NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ---------------- #

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("home"))
    return redirect(url_for("login"))

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("home"))

    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if user and user["password"] == password:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)

# REGISTER (so you can create user)
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
        except:
            conn.close()
            return "User already exists"

        conn.close()
        return redirect(url_for("login"))

    return render_template("register.html")

# HOME
@app.route("/home")
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    page = request.args.get("page", "dashboard")
    analytics_data = None

    if page == "analytics":
        conn = get_db_connection()

        total_time = conn.execute(
            "SELECT SUM(duration) FROM sessions WHERE username = ?",
            (session["user"],)
        ).fetchone()[0]

        total_sessions = conn.execute(
            "SELECT COUNT(*) FROM sessions WHERE username = ?",
            (session["user"],)
        ).fetchone()[0]

        recent_sessions = conn.execute(
            "SELECT duration, date FROM sessions WHERE username = ? ORDER BY date DESC LIMIT 5",
            (session["user"],)
        ).fetchall()

        conn.close()

        if total_time is None:
            total_time = 0

        analytics_data = {
            "total_time": total_time,
            "total_sessions": total_sessions,
            "recent_sessions": recent_sessions
        }

    return render_template(
        "home_page.html",
        username=session["user"],
        page=page,
        analytics=analytics_data
    )
# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/save_session", methods=["POST"])
def save_session():
    if "user" not in session:
        return redirect(url_for("login"))

    duration = request.form.get("duration")

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO sessions (username, duration) VALUES (?, ?)",
        (session["user"], duration)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("home", page="analytics"))

if __name__ == "__main__":
    app.run(debug=True)