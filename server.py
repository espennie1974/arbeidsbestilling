from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from datetime import datetime
import os

app = Flask(__name__, static_folder="static")

DB_NAME = "tasks.db"

# Opprett database hvis den ikke finnes
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            created_by TEXT,
            assigned_to TEXT,
            status TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Rute for hovedsiden
@app.route("/")
def home():
    return send_from_directory(".", "index.html")

# Hent alle oppgaver
@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM tasks")
    rows = c.fetchall()
    conn.close()

    tasks = []
    for row in rows:
        tasks.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "created_by": row[3],
            "assigned_to": row[4],
            "status": row[5],
            "created_at": row[6]
        })
    return jsonify(tasks)

# Legg til en ny oppgave
@app.route("/add_task", methods=["POST"])
def add_task():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    created_by = data.get("created_by", "Ukjent")
    assigned_to = data.get("assigned_to", "Ikke tildelt")
    status = data.get("status", "Aktiv")
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO tasks (title, description, created_by, assigned_to, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, description, created_by, assigned_to, status, created_at))
    conn.commit()
    conn.close()

    return jsonify({"message": "Oppdrag lagt til!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
