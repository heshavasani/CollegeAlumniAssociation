from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
from datetime import datetime

alapp = Flask(__name__)
CORS(alapp)

DB_NAME = "database.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_db()
    cur = conn.cursor()
    
    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(100) NOT NULL UNIQUE,
            email VARCHAR(120) NOT NULL,
            password_hash VARCHAR(200) NOT NULL,
            role VARCHAR(20) NOT NULL,
            department VARCHAR(100),
            batch_year INTEGER,
            linkedin_url VARCHAR(200),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Messages table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

# SIGNUP ENDPOINT
@alapp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    
    # Extract data
    username = data.get("username")
    email = data.get("mail")
    password = data.get("pass")
    role = data.get("role")
    department = data.get("dept")
    batch_year = data.get("year")
    
    # Validate required fields
    if not all([username, email, password, role]):
        return jsonify({"message": "Missing required fields"}), 400
    
    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Check if username already exists
        existing = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            conn.close()
            return jsonify({"message": "Username already exists"}), 400
        
        # Hash password and insert user
        hashed_pw = hash_password(password)
        cur.execute("""
            INSERT INTO users (username, email, password_hash, role, department, batch_year)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, email, hashed_pw, role, department, batch_year))
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Signup successful"}), 201
        
    except Exception as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500

# LOGIN ENDPOINT
@alapp.route("/login", methods=["POST"])
def login():
    data = request.json
    
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400
    
    try:
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", 
            (username,)
        ).fetchone()
        conn.close()
        
        if not user:
            return jsonify({"message": "Invalid username or password"}), 401
        
        # Verify password
        hashed_pw = hash_password(password)
        if user["password_hash"] != hashed_pw:
            return jsonify({"message": "Invalid username or password"}), 401
        
        # Return user data with role for frontend routing
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "role": user["role"],
                "department": user["department"],
                "batch_year": user["batch_year"]
            }
        }), 200
        
    except Exception as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500

# EXISTING MESSAGE ENDPOINTS
@alapp.route("/send", methods=["POST"])
def send_message():
    data = request.json
    conn = get_db()
    conn.execute(
        "INSERT INTO messages (sender, receiver, content) VALUES (?, ?, ?)",
        (data["sender"], data["receiver"], data["content"])
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@alapp.route("/messages/<sender>/<receiver>")
def get_messages(sender, receiver):
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM messages
        WHERE (sender=? AND receiver=?)
           OR (sender=? AND receiver=?)
        ORDER BY timestamp
    """, (sender, receiver, receiver, sender)).fetchall()
    conn.close()

    return jsonify([
        {
            "sender": r["sender"],
            "receiver": r["receiver"],
            "content": r["content"],
            "time": r["timestamp"]
        } for r in rows
    ])

if __name__ == "__main__":
    # Run signup on port 5000 and login on port 5001
    # You'll need to run two instances or update your frontend
    alapp.run(debug=True, port=5000)