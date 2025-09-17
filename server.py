from flask import Flask, request, jsonify, render_template
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

DB_NAME = "tasks.db"

# --- Hjelpefunksjon for database ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            created_by TEXT,
            assigned_to TEXT,
            status TEXT DEFAULT 'Aktiv',
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

# --- Ruter ---
@app.route("/")
def index():
    return render_template("index.html")

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

@app.route("/add_task", methods=["POST"])
def add_task():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    created_by = data.get("created_by", "Ukjent")
    assigned_to = data.get("assigned_to", "Ikke tildelt")
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO tasks (title, description, created_by, assigned_to, status, created_at)
        VALUES (?, ?, ?, ?, 'Aktiv', ?)
    """, (title, description, created_by, assigned_to, created_at))
    conn.commit()
    conn.close()

    return jsonify({"message": "Oppdrag lagt til!"})

@app.route("/update_status/<int:task_id>", methods=["POST"])
def update_status(task_id):
    data = request.get_json()
    new_status = data.get("status", "Aktiv")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Status oppdatert!"})

@app.route("/delete_task/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Oppdrag slettet!"})

# --- Start app ---
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
