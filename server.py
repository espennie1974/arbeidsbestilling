from flask import Flask, request, jsonify, render_template
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

# Hent database-URL fra Render miljøvariabel
DATABASE_URL = os.environ.get("DATABASE_URL")

# Funksjon for å koble til databasen
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    return conn

# Opprett tabellen hvis den ikke finnes
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            created_by TEXT,
            assigned_to TEXT,
            status TEXT,
            created_at TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, created_by, assigned_to, status, created_at FROM tasks;")
    tasks = cur.fetchall()
    cur.close()
    conn.close()

    task_list = []
    for row in tasks:
        task_list.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "created_by": row[3],
            "assigned_to": row[4],
            "status": row[5],
            "created_at": row[6].strftime("%Y-%m-%d %H:%M:%S") if row[6] else None
        })
    return jsonify(task_list)

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    title = data.get("title")
    description = data.get("description")
    created_by = data.get("created_by")
    assigned_to = data.get("assigned_to")
    status = "Ny"
    created_at = datetime.now()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, description, created_by, assigned_to, status, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
        (title, description, created_by, assigned_to, status, created_at)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Oppdrag lagt til!"})

if __name__ == "__main__":
    # Opprett tabellen automatisk hvis den ikke finnes
    init_db()

    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
