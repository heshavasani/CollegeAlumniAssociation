from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from datetime import datetime   

register = Flask(__name__)
CORS(register)

register.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
register.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(register)
bcrypt = Bcrypt(register)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(100))
    batch_year = db.Column(db.Integer)
    linkedin_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# insert all the value of user and verify their role

# @register.route("/", methods=["GET", "POST"])
# def home():
#     if request.method == "GET":
#         return "Server working"

#     print("ROUTE HIT")
    
@register.route("/signup", methods=["POST"])
def signupF():
    data = request.get_json()

    username = data.get("username")
    password = data.get("pass")
    mail = data.get("mail")
    role = data.get("role")
    linkedIn = data.get("linkedIn")
    clg_name = data.get("clg_name")
    dept = data.get("dept")

    # username = "labdhi"
    # password = "1234"
    # mail = "labdhi@gmail.com"
    # role = "Student"
    # linkedIn = "https://www.linkedin.com/in/labdhi-shah-1a8308362/"
    # clg_name = "SBMP"
    # dept = "IT"

    try:
        year = int(data.get("year"))
        # year = 2024
    except (TypeError, ValueError):
        return jsonify({"message": "Invalid year"}), 400

    if not username or not password or not mail or not role:
        return jsonify({"message": "Missing required fields"}), 400

    # if email already registered
    existing_user = User.query.filter_by(email=mail).first()
    if existing_user:
        return jsonify({"message": "Email already registered"}), 400
    
    # Role validation
    current_year = datetime.now().year
    if role == "alumni" and year >= current_year:
        return jsonify({"message": "Invalid alumni year"}), 400

    # Hash password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    new_user = User(
        username=username,
        email=mail,
        password_hash=hashed_password,
        role=role,
        department=dept,
        batch_year=year,
        linkedin_url=linkedIn
    )

    db.session.add(new_user)
    db.session.commit()
    print("DONE")

    return jsonify({"message": "Sign Up Successful"})

if __name__ == "__main__":
    with register.app_context():
        db.create_all()
    register.run(debug=True)