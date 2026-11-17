import os
import time
import psycopg2
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

def get_conn():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )

def init_db():
    # Database start hone mein time lagta hai, isliye retry karte hain
    for _ in range(10):
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    course VARCHAR(100) NOT NULL
                )
            """)
            conn.commit()
            cur.close()
            conn.close()
            return
        except psycopg2.OperationalError:
            print("DB ready nahi hai, 3 sec wait...")
            time.sleep(3)
    raise Exception("Database se connect nahi ho paya")

@app.route("/")
def index():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, course FROM students ORDER BY id DESC")
    students = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", students=students)

@app.route("/register", methods=["POST"])
def register():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students (name, email, course) VALUES (%s, %s, %s)",
        (request.form["name"], request.form["email"], request.form["course"]),
    )
    conn.commit()
    cur.close()
    conn.close()
    return redirect("/")

# gunicorn / flask dono ke liye DB table pehle bana do
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
