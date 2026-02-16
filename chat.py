from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# --- MODELS ---

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(100))
    college = db.Column(db.String(200), default="Not Set")
    batch_year = db.Column(db.String(50))

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --- ROUTES ---

@app.route("/chat-users/<int:current_user_id>", methods=["GET"])
def get_chat_users(current_user_id):
    search_query = request.args.get('search', '').strip()
    try:
        if search_query:
            # GLOBAL SEARCH
            users = User.query.filter(
                (User.id != current_user_id) & 
                (User.username.ilike(f"%{search_query}%"))
            ).all()
        else:
            # CHAT HISTORY ONLY
            sent_ids = db.session.query(Message.receiver_id).filter(Message.sender_id == current_user_id)
            recv_ids = db.session.query(Message.sender_id).filter(Message.receiver_id == current_user_id)
            history_ids = [id_tuple[0] for id_tuple in sent_ids.union(recv_ids).all()]
            users = User.query.filter(User.id.in_(history_ids)).all()
        
        return jsonify([{
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "dept": u.department
        } for u in users]), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/get-messages/<int:u1>/<int:u2>", methods=["GET"])
def get_messages(u1, u2):
    msgs = Message.query.filter(
        ((Message.sender_id == u1) & (Message.receiver_id == u2)) |
        ((Message.sender_id == u2) & (Message.receiver_id == u1))
    ).order_by(Message.timestamp.asc()).all()
    
    return jsonify([{
        "sender": m.sender_id,
        "content": m.content,
        "time": m.timestamp.strftime("%H:%M")
    } for m in msgs]), 200

@app.route("/send-message", methods=["POST"])
def send_message():
    data = request.get_json()
    try:
        new_msg = Message(
            sender_id=data['sender'],
            receiver_id=data['receiver'],
            content=data['content']
        )
        db.session.add(new_msg)
        db.session.commit()
        return jsonify({"ok": True}), 201
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

# Added profile route to support your S_profile.html
@app.route("/get-profile/<int:user_id>", methods=["GET"])
def get_profile(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            "username": user.username,
            "role": user.role,
            "department": user.department,
            "college": user.college,
            "batch_year": user.batch_year,
            "skills": [] # You can add a Skill model/query here later
        }), 200
    return jsonify({"message": "User not found"}), 404

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)