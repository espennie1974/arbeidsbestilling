import os
import psycopg2
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Hent database-URL fra miljøvariabel
DATABASE_URL = os.environ.get("DATABASE_URL")
print("=== Bruker denne DATABASE_URL ===")
print(DATABASE_URL)


def get_db_connection():
    """Koble til databasen"""
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        print("✅ Database-tilkobling OK")
        return conn
    except Exception as e:
        print("❌ Feil ved tilkobling til databasen:", e)
        raise


def init_db():
    """Opprett tabell hvis den ikke finnes"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        print("⚙️ Oppretter tabell hvis den ikke finnes...")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS oppdrag (
                id SERIAL PRIMARY KEY,
                tittel TEXT NOT NULL,
                beskrivelse TEXT,
                status TEXT DEFAULT 'Ny'
            );
        """)

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Tabell klar")
    except Exception as e:
        print("❌ Klarte ikke å opprette tabell:", e)
        raise


@app.route('/')
def index():
    """Vis hovedsiden"""
    return render_template('index.html')


@app.route('/test')
def test():
    """Test-endepunkt for å sjekke om appen kjører"""
    return jsonify({"status": "API kjører 🚀"})


@app.route('/dbtest')
def dbtest():
    """Test database-tilkobling"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"database": "OK ✅"})
    except Exception as e:
        return jsonify({"database": "Feil ❌", "detaljer": str(e)}), 500


@app.route('/api/oppdrag', methods=['GET'])
def hent_oppdrag():
    """Hent alle oppdrag"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, tittel, beskrivelse, status FROM oppdrag ORDER BY id DESC;")
        oppdrag = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(oppdrag)
    except Exception as e:
        print("❌ Feil ved henting av oppdrag:", e)
        return jsonify({"error": "Kunne ikke hente oppdrag"}), 500


@app.route('/api/oppdrag', methods=['POST'])
def legg_til_oppdrag():
    """Legg til nytt oppdrag"""
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO oppdrag (tittel, beskrivelse, status) VALUES (%s, %s, %s) RETURNING id;",
            (data['tittel'], data['beskrivelse'], data.get('status', 'Ny'))
        )
        oppdrag_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"id": oppdrag_id}), 201
    except Exception as e:
        print("❌ Feil ved innsending av oppdrag:", e)
        return jsonify({"error": "Kunne ikke legge til oppdrag"}), 500


@app.route('/api/oppdrag/<int:oppdrag_id>', methods=['PUT'])
def oppdater_status(oppdrag_id):
    """Oppdater status på et oppdrag"""
    data = request.json
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE oppdrag SET status = %s WHERE id = %s;",
            (data['status'], oppdrag_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "oppdatert"})
    except Exception as e:
        print("❌ Feil ved oppdatering av oppdrag:", e)
        return jsonify({"error": "Kunne ikke oppdatere oppdrag"}), 500


if __name__ == '__main__':
    try:
        init_db()  # Sørg for at tabellen finnes
    except Exception as e:
        print("⚠️ Appen starter uten å opprette tabell:", e)

    app.run(host='0.0.0.0', port=5000)
