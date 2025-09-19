from flask import Flask, render_template, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Hent database-URL fra Render miljøvariabel
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    return conn

def init_db():
    """Oppretter tabellen hvis den ikke finnes"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            created_by TEXT,
            assigned_to TEXT,
            status TEXT DEFAULT 'Ny'
        );
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
    cur.execute("SELECT id, title, description, created_by, assigned_to, status FROM tasks;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    tasks = []
    for row in rows:
        tasks.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "created_by": row[3],
            "assigned_to": row[4],
            "status": row[5]
        })
    return jsonify(tasks)

@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.json
    title = data.get("title")
    description = data.get("description")
    created_by = data.get("created_by")
    assigned_to = data.get("assigned_to")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, description, created_by, assigned_to) VALUES (%s, %s, %s, %s) RETURNING id;",
        (title, description, created_by, assigned_to)
    )
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"id": task_id, "title": title, "description": description, "created_by": created_by, "assigned_to": assigned_to, "status": "Ny"})

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json
    status = data.get("status")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET status = %s WHERE id = %s;", (status, task_id))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"id": task_id, "status": status})

if __name__ == "__main__":
    init_db()  # Opprett tabell ved oppstart
    app.run(host="0.0.0.0", port=5000, debug=True)
