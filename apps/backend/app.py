import os
import time
import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "kubepilot")
DB_USER = os.getenv("DB_USER", "kubepilot")
DB_PASSWORD = os.getenv("DB_PASSWORD", "kubepilot")
DB_PORT = os.getenv("DB_PORT", "5432")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )


def wait_for_database():
    retries = 20

    while retries > 0:
        try:
            conn = get_connection()
            conn.close()
            print("Database connection successful")
            return
        except Exception as error:
            print(f"Waiting for database... {error}")
            retries -= 1
            time.sleep(3)

    raise Exception("Could not connect to database")


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Welcome to KubePilot Backend API",
        "service": "kubepilot-backend",
        "endpoints": {
            "health": "/health",
            "readiness": "/ready",
            "tasks": "/api/tasks"
        }
    }), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "kubepilot-backend"
    }), 200


@app.route("/ready", methods=["GET"])
def ready():
    try:
        conn = get_connection()
        conn.close()

        return jsonify({
            "status": "ready",
            "database": "connected"
        }), 200

    except Exception as error:
        return jsonify({
            "status": "not ready",
            "database": "disconnected",
            "error": str(error)
        }), 503


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, title, status, created_at FROM tasks ORDER BY id DESC;")
    rows = cur.fetchall()

    tasks = []

    for row in rows:
        tasks.append({
            "id": row[0],
            "title": row[1],
            "status": row[2],
            "created_at": row[3].isoformat()
        })

    cur.close()
    conn.close()

    return jsonify(tasks), 200


@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()

    if not data or "title" not in data:
        return jsonify({
            "error": "Task title is required"
        }), 400

    title = data["title"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, status, created_at;",
        (title,)
    )

    row = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()

    task = {
        "id": row[0],
        "title": row[1],
        "status": row[2],
        "created_at": row[3].isoformat()
    }

    return jsonify(task), 201


if __name__ == "__main__":
    wait_for_database()
    init_db()
    app.run(host="0.0.0.0", port=5000)
