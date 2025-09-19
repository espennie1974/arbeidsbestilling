import os
import psycopg2
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Hent database-url fra Render sine miljøvariabler
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    return conn

def init_db():
    """Opprett tabellen tasks hvis den ikke finnes, og logg hvor mange oppdrag som finnes"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Ny',
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()

    # Tell antall rader
    cur.execute("SELECT COUNT(*) FROM tasks;")
    count = cur.fetchone()[0]
    print(f"✅ Tabell 'tasks' er klar. Antall eksisterende oppdrag: {count}")

    cur.close()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, description, status, created_by, created_at FROM tasks ORDER BY created_at DESC;")
    tasks = cur.fetchall()
    cur.close()
    conn.close()

    task_list = []
    for row in tasks:
        task_list.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "status": row[3],
            "created_by": row[4],
            "created_at": row[5].strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify(task_list)

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    created_by = data.get("created_by")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, description, created_by) VALUES (%s, %s, %s) RETURNING id;",
        (title, description, created_by)
    )
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"id": task_id, "title": title, "description": description, "created_by": created_by, "status": "Ny"})

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    status = data.get("status")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET status = %s WHERE id = %s;", (status, task_id))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"id": task_id, "status": status})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
