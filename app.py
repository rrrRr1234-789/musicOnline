from functools import wraps
import sqlite3
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from markupsafe import escape
from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "database" / "musicOnline.sqlite3"

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-change-this-secret-key"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_one(sql, params=()):
    return get_db().execute(sql, params).fetchone()


def query_all(sql, params=()):
    return get_db().execute(sql, params).fetchall()


def execute(sql, params=()):
    db = get_db()
    db.execute(sql, params)
    db.commit()


def init_db():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS publicUsers (
            userID INTEGER PRIMARY KEY AUTOINCREMENT,
            firstName TEXT NOT NULL,
            surname TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phoneNo TEXT,
            password TEXT NOT NULL,
            salt TEXT,
            dateRegistered TEXT NOT NULL DEFAULT CURRENT_DATE
        );

        CREATE TABLE IF NOT EXISTS admin (
            adminID INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            dateCreated TEXT NOT NULL DEFAULT CURRENT_DATE
        );

        CREATE TABLE IF NOT EXISTS vinyls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist TEXT NOT NULL,
            album TEXT NOT NULL,
            recordType TEXT NOT NULL,
            releaseDate TEXT,
            year INTEGER,
            genre TEXT,
            condition TEXT,
            price REAL NOT NULL,
            description TEXT,
            albumCover TEXT,
            status TEXT NOT NULL DEFAULT 'Visible',
            dateAdded TEXT NOT NULL DEFAULT CURRENT_DATE,
            userID INTEGER NOT NULL,
            FOREIGN KEY (userID) REFERENCES publicUsers(userID)
        );
        """
    )

    user_count = db.execute("SELECT COUNT(*) FROM publicUsers").fetchone()[0]
    if user_count == 0:
        users = [
            ("Shi", "Linran", "user1@musiconline.com", "13800000001", generate_password_hash("User12345")),
            ("Alex", "Taylor", "user2@musiconline.com", "13800000002", generate_password_hash("User12345")),
        ]
        db.executemany(
            "INSERT INTO publicUsers (firstName, surname, email, phoneNo, password) VALUES (?, ?, ?, ?, ?)",
            users,
        )

    admin_count = db.execute("SELECT COUNT(*) FROM admin").fetchone()[0]
    if admin_count == 0:
        admins = [
            ("admin1", "admin1@musiconline.com", generate_password_hash("Admin12345"), "superadmin"),
            ("admin2", "admin2@musiconline.com", generate_password_hash("Admin12345"), "moderator"),
        ]
        db.executemany(
            "INSERT INTO admin (username, email, password, role) VALUES (?, ?, ?, ?)",
            admins,
        )

    vinyl_count = db.execute("SELECT COUNT(*) FROM vinyls").fetchone()[0]
    if vinyl_count == 0:
        records = [
            ("The Beatles", "Abbey Road", "Album", "1969-09-26", 1969, "Rock", "Very Good", 39.99),
            ("Pink Floyd", "The Dark Side of the Moon", "Album", "1973-03-01", 1973, "Rock", "Good", 34.50),
            ("Fleetwood Mac", "Rumours", "Album", "1977-02-04", 1977, "Rock", "Very Good", 29.99),
            ("Michael Jackson", "Thriller", "Album", "1982-11-30", 1982, "Pop", "Good", 24.99),
            ("Nirvana", "Nevermind", "Album", "1991-09-24", 1991, "Grunge", "Very Good", 32.00),
            ("David Bowie", "Heroes", "Album", "1977-10-14", 1977, "Rock", "Good", 28.50),
            ("Daft Punk", "Random Access Memories", "Album", "2013-05-17", 2013, "Dance", "New", 35.00),
            ("Radiohead", "OK Computer", "Album", "1997-05-21", 1997, "Indie", "Very Good", 31.99),
            ("Metallica", "Master of Puppets", "Album", "1986-03-03", 1986, "Metal", "Good", 27.99),
            ("Queen", "A Night at the Opera", "Album", "1975-11-21", 1975, "Rock", "Very Good", 30.50),
            ("Prince", "Purple Rain", "Album", "1984-06-25", 1984, "Pop", "Good", 26.00),
            ("The Smiths", "The Queen Is Dead", "Album", "1986-06-16", 1986, "Indie", "Very Good", 33.50),
            ("Bob Marley", "Legend", "Album", "1984-05-08", 1984, "Reggae", "Good", 22.99),
            ("Madonna", "Like a Virgin", "Album", "1984-11-12", 1984, "Pop", "Good", 21.50),
            ("Arctic Monkeys", "AM", "Album", "2013-09-09", 2013, "Indie", "New", 25.99),
        ]
        db.executemany(
            """
            INSERT INTO vinyls
            (artist, album, recordType, releaseDate, year, genre, condition, price, description, albumCover, userID)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (*r, f"{r[1]} by {r[0]} is listed for sale on musicOnline.", f"cover-{i % 6 + 1}", i % 2 + 1)
                for i, r in enumerate(records)
            ],
        )

    db.commit()
    db.close()


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "userID" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))
        return view(**kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "adminID" not in session:
            flash("Please log in as administrator.")
            return redirect(url_for("admin_login"))
        return view(**kwargs)

    return wrapped_view


@app.before_request
def load_logged_in_user():
    g.user = None
    g.admin = None
    if "userID" in session:
        g.user = query_one("SELECT * FROM publicUsers WHERE userID = ?", (session["userID"],))
    if "adminID" in session:
        g.admin = query_one("SELECT * FROM admin WHERE adminID = ?", (session["adminID"],))


@app.route("/")
def index():
    latest = query_all("SELECT * FROM vinyls ORDER BY dateAdded DESC, id DESC LIMIT 4")
    return render_template("index.html", latest=latest)


@app.route("/search")
def search():
    keyword = request.args.get("q", "").strip()
    records = []
    if keyword:
        like = f"%{keyword}%"
        records = query_all(
            """
            SELECT * FROM vinyls
            WHERE artist LIKE ? OR album LIKE ? OR recordType LIKE ? OR genre LIKE ?
            ORDER BY artist, album
            """,
            (like, like, like, like),
        )
    else:
        records = query_all("SELECT * FROM vinyls ORDER BY dateAdded DESC, id DESC")
    return render_template("search.html", records=records, keyword=escape(keyword))


@app.route("/vinyl/<int:id>")
def vinyl_details(id):
    vinyl = query_one(
        """
        SELECT v.*, u.firstName, u.surname, u.email
        FROM vinyls v
        JOIN publicUsers u ON u.userID = v.userID
        WHERE v.id = ?
        """,
        (id,),
    )
    if vinyl is None:
        flash("Record not found.")
        return redirect(url_for("search"))
    return render_template("vinyl_details.html", vinyl=vinyl)


@app.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        first_name = request.form["firstName"].strip()
        surname = request.form["surname"].strip()
        email = request.form["email"].strip().lower()
        phone = request.form["phoneNo"].strip()
        password = request.form["password"]
        confirm = request.form["confirmPassword"]

        if password != confirm:
            flash("Passwords do not match.")
        elif query_one("SELECT userID FROM publicUsers WHERE email = ?", (email,)):
            flash("This email is already registered.")
        else:
            execute(
                """
                INSERT INTO publicUsers (firstName, surname, email, phoneNo, password)
                VALUES (?, ?, ?, ?, ?)
                """,
                (first_name, surname, email, phone, generate_password_hash(password)),
            )
            flash("Registration successful. Please log in.")
            return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user = query_one("SELECT * FROM publicUsers WHERE email = ?", (email,))
        if user and check_password_hash(user["password"], password):
            session.clear()
            session["userID"] = user["userID"]
            session["userName"] = user["firstName"]
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out.")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    records = query_all("SELECT * FROM vinyls WHERE userID = ? ORDER BY id DESC", (session["userID"],))
    return render_template("dashboard.html", records=records)


@app.route("/vinyl/add", methods=("GET", "POST"))
@login_required
def add_vinyl():
    if request.method == "POST":
        save_vinyl(request.form, session["userID"])
        flash("Vinyl record added.")
        return redirect(url_for("dashboard"))
    return render_template("vinyl_form.html", vinyl=None, title="Add Vinyl")


@app.route("/vinyl/edit/<int:id>", methods=("GET", "POST"))
@login_required
def edit_vinyl(id):
    vinyl = query_one("SELECT * FROM vinyls WHERE id = ? AND userID = ?", (id, session["userID"]))
    if vinyl is None:
        flash("You can only edit your own records.")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        update_vinyl(request.form, id, session["userID"])
        flash("Vinyl record updated.")
        return redirect(url_for("dashboard"))
    return render_template("vinyl_form.html", vinyl=vinyl, title="Edit Vinyl")


@app.route("/vinyl/delete/<int:id>", methods=("GET", "POST"))
@login_required
def delete_vinyl(id):
    vinyl = query_one("SELECT * FROM vinyls WHERE id = ? AND userID = ?", (id, session["userID"]))
    if vinyl is None:
        flash("You can only delete your own records.")
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        execute("DELETE FROM vinyls WHERE id = ? AND userID = ?", (id, session["userID"]))
        flash("Vinyl record deleted.")
        return redirect(url_for("dashboard"))
    return render_template("delete_confirm.html", vinyl=vinyl)


@app.route("/admin/login", methods=("GET", "POST"))
def admin_login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        admin = query_one("SELECT * FROM admin WHERE username = ? OR email = ?", (username, username))
        if admin and check_password_hash(admin["password"], password):
            session.clear()
            session["adminID"] = admin["adminID"]
            return redirect(url_for("admin_dashboard"))
        flash("Invalid administrator credentials.")
    return render_template("admin_login.html")


@app.route("/admin")
@admin_required
def admin_dashboard():
    total_vinyls = query_one("SELECT COUNT(*) AS count FROM vinyls")["count"]
    total_users = query_one("SELECT COUNT(*) AS count FROM publicUsers")["count"]
    records = query_all("SELECT * FROM vinyls ORDER BY id DESC LIMIT 8")
    return render_template(
        "admin_dashboard.html",
        total_vinyls=total_vinyls,
        total_users=total_users,
        records=records,
    )


@app.route("/admin/records")
@admin_required
def admin_records():
    records = query_all("SELECT * FROM vinyls ORDER BY id DESC")
    return render_template("admin_records.html", records=records)


@app.route("/admin/records/add", methods=("GET", "POST"))
@admin_required
def admin_add_record():
    if request.method == "POST":
        save_vinyl(request.form, 1)
        flash("Admin record added.")
        return redirect(url_for("admin_records"))
    return render_template("vinyl_form.html", vinyl=None, title="Admin Add Record", admin_mode=True)


@app.route("/admin/records/edit/<int:id>", methods=("GET", "POST"))
@admin_required
def admin_edit_record(id):
    vinyl = query_one("SELECT * FROM vinyls WHERE id = ?", (id,))
    if vinyl is None:
        flash("Record not found.")
        return redirect(url_for("admin_records"))
    if request.method == "POST":
        update_vinyl(request.form, id, None)
        flash("Admin record updated.")
        return redirect(url_for("admin_records"))
    return render_template("vinyl_form.html", vinyl=vinyl, title="Admin Edit Record", admin_mode=True)


@app.route("/admin/records/delete/<int:id>", methods=("POST",))
@admin_required
def admin_delete_record(id):
    execute("DELETE FROM vinyls WHERE id = ?", (id,))
    flash("Admin record deleted.")
    return redirect(url_for("admin_records"))


def save_vinyl(form, user_id):
    execute(
        """
        INSERT INTO vinyls
        (artist, album, recordType, releaseDate, year, genre, condition, price, description, albumCover, userID)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        vinyl_params(form) + (user_id,),
    )


def update_vinyl(form, record_id, user_id=None):
    params = vinyl_params(form) + (record_id,)
    sql = """
        UPDATE vinyls
        SET artist = ?, album = ?, recordType = ?, releaseDate = ?, year = ?,
            genre = ?, condition = ?, price = ?, description = ?, albumCover = ?
        WHERE id = ?
    """
    if user_id is not None:
        sql += " AND userID = ?"
        params += (user_id,)
    execute(sql, params)


def vinyl_params(form):
    release_date = form.get("releaseDate") or None
    year = int(release_date[:4]) if release_date else int(form.get("year") or 2026)
    return (
        form["artist"].strip(),
        form["album"].strip(),
        form.get("recordType", "Album").strip(),
        release_date,
        year,
        form.get("genre", "").strip(),
        form.get("condition", "").strip(),
        float(form["price"]),
        form.get("description", "").strip(),
        form.get("albumCover", "cover-1"),
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
