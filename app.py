from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import sqlite3, os, csv, io, random
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
DB_PATH = os.path.join(os.path.dirname(__file__), "nutrition.db")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'user')""")
    conn.execute("""CREATE TABLE IF NOT EXISTS surveys (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER, gender TEXT,
        occupation TEXT, fruit_intake TEXT, vegetables TEXT, protein_food TEXT,
        junk_food TEXT, weakness TEXT, symptoms TEXT, supplements TEXT,
        skip_meals TEXT, nutrition_awareness TEXT, risk_level TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        conn.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
                     ("admin", generate_password_hash("admin123"), "admin"))
        conn.execute("INSERT INTO users(username,password_hash,role) VALUES(?,?,?)",
                     ("user", generate_password_hash("user123"), "user"))
    if conn.execute("SELECT COUNT(*) FROM surveys").fetchone()[0] == 0:
        seed_sample_data(conn, 500)
    conn.commit()
    conn.close()

def risk_score(row):
    score = 0
    if row.get("fruit_intake") in ("Never", "Rarely"): score += 2
    elif row.get("fruit_intake") == "3-4 times/week": score += 1
    if row.get("vegetables") in ("Rarely", "Never"): score += 2
    elif row.get("vegetables") == "3-4 times/week": score += 1
    if row.get("protein_food") == "Rarely": score += 2
    elif row.get("protein_food") == "Sometimes": score += 1
    if row.get("junk_food") == "Daily": score += 2
    elif row.get("junk_food") == "Sometimes": score += 1
    if row.get("weakness") == "Yes": score += 2
    if row.get("symptoms") == "Yes": score += 2
    if row.get("skip_meals") == "Yes": score += 1
    if row.get("supplements") == "No": score += 1
    return "High" if score >= 9 else ("Medium" if score >= 5 else "Low")

def seed_sample_data(conn, count):
    random.seed(42)
    names = ["Aarav", "Aanya", "Ishaan", "Diya", "Rohan", "Sana", "Kabir", "Meera", "Arjun", "Anaya",
             "Rahul", "Priya", "Vivek", "Neha", "Karan", "Pooja", "Om", "Sara", "Aditya", "Ira"]
    choices = {
      "fruit_intake": ["Daily", "3-4 times/week", "Rarely", "Never"],
      "vegetables": ["Daily", "3-4 times/week", "Rarely"],
      "protein_food": ["Daily", "Sometimes", "Rarely"],
      "junk_food": ["Daily", "Sometimes", "Rarely"],
      "yesno": ["Yes", "No"]
    }
    for i in range(count):
        r = {
          "name": random.choice(names) + " " + random.choice(["Sharma","Patel","Khan","Singh","Das","Joshi","More","Rao"]),
          "age": random.randint(15, 70), "gender": random.choice(["Male","Female","Other"]),
          "occupation": random.choice(["Student","Employee","Self-employed","Homemaker","Other"]),
          "fruit_intake": random.choice(choices["fruit_intake"]),
          "vegetables": random.choice(choices["vegetables"]),
          "protein_food": random.choice(choices["protein_food"]),
          "junk_food": random.choice(choices["junk_food"]),
          "weakness": random.choice(choices["yesno"]),
          "symptoms": random.choice(choices["yesno"]),
          "supplements": random.choice(choices["yesno"]),
          "skip_meals": random.choice(choices["yesno"]),
          "nutrition_awareness": random.choice(choices["yesno"])
        }
        level = risk_score(r)
        conn.execute("""INSERT INTO surveys(name,age,gender,occupation,fruit_intake,vegetables,protein_food,junk_food,
          weakness,symptoms,supplements,skip_meals,nutrition_awareness,risk_level)
          VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
          (r["name"],r["age"],r["gender"],r["occupation"],r["fruit_intake"],r["vegetables"],r["protein_food"],
           r["junk_food"],r["weakness"],r["symptoms"],r["supplements"],r["skip_meals"],r["nutrition_awareness"],level))

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Admin access is required.", "danger")
            return redirect(url_for("dashboard"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    conn = db()
    total = conn.execute("SELECT COUNT(*) FROM surveys").fetchone()[0]
    high = conn.execute("SELECT COUNT(*) FROM surveys WHERE risk_level='High'").fetchone()[0]
    conn.close()
    return render_template("home.html", total=total, high=high)

@app.route("/survey", methods=["GET","POST"])
def survey():
    if request.method == "POST":
        r = {k: request.form.get(k, "").strip() for k in [
            "name","age","gender","occupation","fruit_intake","vegetables","protein_food",
            "junk_food","weakness","symptoms","supplements","skip_meals","nutrition_awareness"]}
        try:
            age = int(r["age"])
            if not r["name"] or age < 1 or age > 120: raise ValueError()
        except ValueError:
            flash("Enter a name and a valid age (1–120).", "danger")
            return render_template("survey.html", form=r)
        r["risk_level"] = risk_score(r)
        conn = db()
        conn.execute("""INSERT INTO surveys(name,age,gender,occupation,fruit_intake,vegetables,protein_food,junk_food,
          weakness,symptoms,supplements,skip_meals,nutrition_awareness,risk_level)
          VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
          (r["name"],age,r["gender"],r["occupation"],r["fruit_intake"],r["vegetables"],r["protein_food"],
           r["junk_food"],r["weakness"],r["symptoms"],r["supplements"],r["skip_meals"],r["nutrition_awareness"],r["risk_level"]))
        conn.commit(); conn.close()
        return render_template("result.html", result=r)
    return render_template("survey.html", form={})

@app.route("/risk")
def risk():
    return render_template("risk.html")

@app.route("/dashboard")
@login_required
def dashboard():
    conn = db()
    rows = conn.execute("SELECT * FROM surveys ORDER BY id DESC").fetchall()
    total = len(rows)
    levels = {level: sum(1 for r in rows if r["risk_level"] == level) for level in ["Low","Medium","High"]}
    gender = {}
    for r in rows: gender[r["gender"]] = gender.get(r["gender"],0)+1
    age_groups = {"15-24":0,"25-34":0,"35-44":0,"45-59":0,"60+":0}
    for r in rows:
        a = r["age"]
        key = "15-24" if a <= 24 else "25-34" if a <= 34 else "35-44" if a <= 44 else "45-59" if a <= 59 else "60+"
        age_groups[key] += 1
    symptom_yes = sum(1 for r in rows if r["symptoms"] == "Yes")
    weak_yes = sum(1 for r in rows if r["weakness"] == "Yes")
    recent = rows[:10]
    conn.close()
    return render_template("dashboard.html", total=total, levels=levels, gender=gender,
                           age_groups=age_groups, symptom_yes=symptom_yes, weak_yes=weak_yes, recent=recent)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        conn = db()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]; session["username"] = user["username"]; session["role"] = user["role"]
            flash("Login successful.", "success")
            return redirect(url_for("admin") if user["role"] == "admin" else url_for("dashboard"))
        flash("Incorrect username or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

@app.route("/admin")
@login_required
@admin_required
def admin():
    conn = db()
    rows = conn.execute("SELECT * FROM surveys ORDER BY id DESC").fetchall()
    total = conn.execute("SELECT COUNT(*) FROM surveys").fetchone()[0]
    users = conn.execute("SELECT id,username,role FROM users ORDER BY id").fetchall()
    conn.close()
    return render_template("admin.html", rows=rows, total=total, users=users)

@app.route("/admin/delete/<int:survey_id>", methods=["POST"])
@login_required
@admin_required
def delete_survey(survey_id):
    conn = db(); conn.execute("DELETE FROM surveys WHERE id=?", (survey_id,)); conn.commit(); conn.close()
    flash("Survey record deleted.", "success")
    return redirect(url_for("admin"))

@app.route("/admin/export")
@login_required
@admin_required
def export_csv():
    conn = db()
    rows = conn.execute("SELECT * FROM surveys ORDER BY id").fetchall()
    conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    if rows:
        writer.writerow(rows[0].keys())
        for row in rows: writer.writerow(list(row))
    mem = io.BytesIO(output.getvalue().encode("utf-8-sig"))
    mem.seek(0)
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="nutrition_survey_data.csv")

@app.route("/admin/upload", methods=["POST"])
@login_required
@admin_required
def upload_csv():
    file = request.files.get("file")
    if not file or not file.filename.lower().endswith(".csv"):
        flash("Please choose a CSV file.", "danger")
        return redirect(url_for("admin"))
    try:
        text = file.stream.read().decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        conn = db(); inserted = 0
        for row in reader:
            def get(*keys, default=""):
                for key in keys:
                    for actual in row:
                        if actual and actual.strip().lower() == key.lower():
                            return (row[actual] or default).strip()
                return default
            r = {
              "name": get("name","what is your name", default="Survey participant"),
              "age": get("age","1. what is your age", default="18"),
              "gender": get("gender","what is your gender", default="Other"),
              "occupation": get("occupation","what is your occupation", default="Other"),
              "fruit_intake": get("fruit_intake","how often do you eat fruits", default="Rarely"),
              "vegetables": get("vegetables","how often do you eat green leafy vegetables", default="Rarely"),
              "protein_food": get("protein_food","protein foods eggs/fish/meat", default="Sometimes"),
              "junk_food": get("junk_food","packaged/junk food", default="Sometimes"),
              "weakness": get("weakness","tired/weak frequently", default="No"),
              "symptoms": get("symptoms","hair fall/pale skin/weak nails", default="No"),
              "supplements": get("supplements","iron/vitamin/mineral supplements", default="No"),
              "skip_meals": get("skip_meals","skip meals", default="No"),
              "nutrition_awareness": get("nutrition_awareness","knows nutritional deficiency", default="No")
            }
            try: age = max(1, min(120, int(float(r["age"]))))
            except: age = 18
            # Normalize common form responses
            for field in ["fruit_intake","vegetables","protein_food","junk_food","weakness","symptoms","supplements","skip_meals","nutrition_awareness"]:
                r[field] = r[field].replace(" times a week"," times/week")
                if r[field].lower() in ("yes","yes."): r[field] = "Yes"
                if r[field].lower() in ("no","no."): r[field] = "No"
            level = risk_score(r)
            conn.execute("""INSERT INTO surveys(name,age,gender,occupation,fruit_intake,vegetables,protein_food,junk_food,
              weakness,symptoms,supplements,skip_meals,nutrition_awareness,risk_level)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
              (r["name"],age,r["gender"],r["occupation"],r["fruit_intake"],r["vegetables"],r["protein_food"],r["junk_food"],
               r["weakness"],r["symptoms"],r["supplements"],r["skip_meals"],r["nutrition_awareness"],level))
            inserted += 1
        conn.commit(); conn.close()
        flash(f"Imported {inserted} survey rows. Please verify column names and response options.", "success")
    except Exception as e:
        flash("Could not read this CSV. Save it as UTF-8 CSV and try again.", "danger")
    return redirect(url_for("admin"))

with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True)
