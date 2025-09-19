from flask import Flask, render_template, request, jsonify
import psycopg2
import psycopg2.errors
import os

app = Flask(__name__)

# Hent database-info fra miljøvariabel
DATABASE_URL = os.environ.get("DATABASE_URL")
print("=== Bruker denne DATABASE_URL ===")
print(DATABASE_URL)

# Ekstra: lag en connection string uten databasenavn (for å kunne opprette databasen)
def get_base_connection():
    """Koble til server uten å spesifisere database, for å opprette database hvis den mangler"""
    parts = DATABASE_URL.rsplit("/", 1)
    base_url = parts[0] + "/postgres"  # prøv å koble til postgres som systemdatabase
    return psycopg2.connect(base_url, sslmode="require")

def ensure_database():
    """Opprett selve databasen hvis den mangler"""
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        conn.close()
        print("✅ Databasen finnes allerede")
    except psycopg2.OperationalError as e:
        if "does not exist" in str(e):
            print("⚠️ Databasen mangler, oppretter arbeidsbestilling_db...")
            conn = get_base_connection()
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("CREATE DATABASE arbeidsbestilling_db;")
            cur.close()
            conn.close()
            print("✅ Databasen ble opprettet")
        else:
            raise

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    return conn

def init_db():
    """Opprett tabellen hvis den ikke finnes"""
    ensure_database()
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
    print("✅ Tabell tasks er klar")

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
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, description, created_by, assigned_to, status) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
        (data["title"], data["description"], data["created_by"], data["assigned_to"], "Ny")
    )
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": task_id}), 201

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE tasks SET status = %s WHERE id = %s;",
        (data["status"], task_id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Task updated"}), 200

if __name__ == "__main__":
    init_db()  # Opprett database og tabell ved oppstart
    app.run(host="0.0.0.0", port=10000, debug=True)
