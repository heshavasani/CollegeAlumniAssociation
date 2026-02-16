from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from registration import db, User  # Ensure registration.py is in the same folder

app = Flask(__name__)
CORS(app)

# Use the same database as your registration app
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the db with this app
db.init_app(app)
bcrypt = Bcrypt(app)

@app.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No data provided"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400

    # 1. Look for user by username
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    # 2. Check password hash
    if bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }), 200
    else:
        return jsonify({"message": "Invalid password"}), 401

if __name__ == "__main__":
    app.run(debug=True, port=5001)
