from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from datetime import datetime

# Initialize app and Extensions
app = Flask(__name__)
CORS(app)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# --- MODELS ---

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
    
    events = db.relationship("Event", backref="creator", lazy=True)
    jobs = db.relationship("Job", backref="poster", lazy=True)
    skills = db.relationship("Skill", backref="owner", lazy=True, cascade="all, delete-orphan")

class Skill(db.Model):
    __tablename__ = "skills"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    college = db.Column(db.String(200))
    department = db.Column(db.String(100))
    batch_year = db.Column(db.Integer)
    skill_name = db.Column(db.String(100), nullable=False)

class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    mode = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(300), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(150), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    paid_status = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posted_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --- ROUTES ---

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Server is running", "status": "ok"}), 200

@app.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["username", "pass", "mail", "role", "dept", "year"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"message": f"Missing required field: {field}"}), 400
        
        username = data["username"]
        password = data["pass"]
        mail = data["mail"]
        role = data["role"]
        dept = data["dept"]
        
        try:
            year = int(data["year"])
        except (ValueError, TypeError):
            return jsonify({"message": "Invalid year format"}), 400

        # Check if email already exists
        if User.query.filter_by(email=mail).first():
            return jsonify({"message": "Email already registered"}), 400
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({"message": "Username already taken"}), 400

        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Create new user
        new_user = User(
            username=username,
            email=mail,
            password_hash=hashed_password,
            role=role,
            department=dept,
            batch_year=year
        )

        db.session.add(new_user)
        db.session.commit()
        
        print(f"✅ New user created: {username} ({role})")
        return jsonify({"message": "Signup Successful"}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Signup error: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        
        if not data or "username" not in data or "password" not in data:
            return jsonify({"message": "Missing username or password"}), 400
        
        username = data["username"]
        password = data["password"]
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"⚠️  Login failed: User '{username}' not found")
            return jsonify({"message": "Invalid credentials"}), 401
        
        # Check password
        if not bcrypt.check_password_hash(user.password_hash, password):
            print(f"⚠️  Login failed: Wrong password for '{username}'")
            return jsonify({"message": "Invalid credentials"}), 401
        
        # Success
        print(f"✅ Login successful: {username} ({user.role})")
        
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "department": user.department,
                "batch_year": user.batch_year
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/get-profile/<int:user_id>", methods=["GET"])
def get_profile(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        # Get college from Skills table
        first_entry = Skill.query.filter_by(user_id=user_id).first()
        college_name = first_entry.college if (first_entry and first_entry.college) else "Not Set"
        
        # Get all skills
        skills = [s.skill_name for s in user.skills if s.skill_name]
        
        return jsonify({
            "username": user.username,
            "role": user.role,
            "department": user.department,
            "batch_year": user.batch_year,
            "college": college_name,
            "skills": skills
        }), 200
        
    except Exception as e:
        print(f"❌ Get profile error: {str(e)}")
        return jsonify({"message": str(e)}), 500

@app.route("/update-profile/<int:user_id>", methods=["PUT"])
def update_profile(user_id):
    try:
        data = request.get_json()
        
        # Clear existing skills
        Skill.query.filter_by(user_id=user_id).delete()
        
        new_skills = data.get("skills", [])
        college = data.get("college", "Not Set")
        
        # Add skills back
        if not new_skills:
            # Even with no skills, store college info
            db.session.add(Skill(user_id=user_id, college=college, skill_name=""))
        else:
            for skill_name in new_skills:
                if skill_name.strip():
                    db.session.add(Skill(
                        user_id=user_id,
                        college=college,
                        skill_name=skill_name.strip()
                    ))
        
        db.session.commit()
        print(f"✅ Profile updated for user {user_id}")
        return jsonify({"message": "Profile updated successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Update profile error: {str(e)}")
        return jsonify({"message": str(e)}), 500

@app.route("/dashboard-stats", methods=["GET"])
def get_dashboard_stats():
    try:
        total_connections = User.query.count()
        total_events = Event.query.count()
        total_jobs = Job.query.count()
        alumni_count = User.query.filter_by(role='alumni').count()
        student_count = User.query.filter_by(role='student').count()
        others_count = total_connections - (alumni_count + student_count)

        return jsonify({
            "connections": total_connections,
            "events_count": total_events,
            "jobs_count": total_jobs,
            "roles": {
                "alumni": alumni_count,
                "students": student_count,
                "others": others_count
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Dashboard stats error: {str(e)}")
        return jsonify({"message": str(e)}), 500

# --- CALENDAR & EVENT ROUTES ---

@app.route("/api/calendar-events", methods=["GET"])
def get_calendar_events():
    """Returns events formatted for calendar pins (simple date + title)"""
    try:
        events = Event.query.all()
        calendar_data = [{
            "id": e.id,
            "title": e.title,
            "start": e.event_date.strftime('%Y-%m-%d'),
            "allDay": True
        } for e in events]
        
        print(f"📅 Returning {len(calendar_data)} calendar events")
        return jsonify(calendar_data), 200
    except Exception as e:
        print(f"❌ Calendar events error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/events", methods=["GET", "POST"])
def handle_events():
    """
    GET: Returns all events with full details for the calendar UI
    POST: Creates a new event
    """
    if request.method == "GET":
        try:
            events = Event.query.order_by(Event.event_date.asc()).all()
            
            events_list = []
            for e in events:
                events_list.append({
                    "id": e.id,
                    "title": e.title,
                    "category": e.mode or "General",
                    "location": e.location or "TBD",
                    "date": e.event_date.strftime('%Y-%m-%d'),
                    "time": e.start_time.strftime('%H:%M') if e.start_time else "TBD",
                    "description": e.description or "",
                    "capacity": e.capacity or 0
                })
            
            print(f"✅ Returning {len(events_list)} events for calendar")
            return jsonify({"success": True, "events": events_list}), 200
            
        except Exception as e:
            print(f"❌ Get events error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    elif request.method == "POST":
        try:
            data = request.get_json()
            print(f"📥 Received event data: {data}")
            
            # Parse date and time
            date_obj = datetime.strptime(data.get('date', data.get('event_date')), '%Y-%m-%d').date()
            
            # Handle time - if not provided, use defaults
            time_str = data.get('time', '09:00')
            start_obj = datetime.strptime(time_str, '%H:%M').time()
            
            # End time defaults to 1 hour after start
            end_obj = datetime.strptime(data.get('end_time', '10:00'), '%H:%M').time()
            
            new_event = Event(
                created_by=data.get('created_by', 1),
                title=data['title'],
                mode=data.get('category', data.get('mode', 'General')),
                location=data.get('location', 'TBD'),
                event_date=date_obj,
                start_time=start_obj,
                end_time=end_obj,
                capacity=int(data.get('capacity', 50)),
                description=data.get('description', '')
            )
            
            db.session.add(new_event)
            db.session.commit()
            
            print(f"✅ Event created: {new_event.title} on {date_obj}")
            return jsonify({"success": True, "message": "Event created successfully"}), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Create event error: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

@app.route("/get-all-events", methods=["GET"])
def get_all_events():
    """Legacy endpoint - returns events list"""
    try:
        events = Event.query.all()
        
        event_list = []
        for ev in events:
            event_list.append({
                "id": ev.id,
                "title": ev.title,
                "mode": ev.mode,
                "location": ev.location,
                "event_date": ev.event_date.strftime('%Y-%m-%d') if hasattr(ev.event_date, 'strftime') else ev.event_date,
                "description": ev.description,
                "capacity": ev.capacity
            })
        
        return jsonify(event_list), 200
    except Exception as e:
        print(f"❌ Get all events error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/get-event/<int:event_id>", methods=["GET"])
def get_event(event_id):
    try:
        ev = Event.query.get(event_id)
        if not ev:
            return jsonify({"message": "Event not found"}), 404
        
        return jsonify({
            "title": ev.title,
            "description": ev.description,
            "date": ev.event_date.strftime("%b %d, %Y"),
            "start_time": ev.start_time.strftime("%H:%M") if ev.start_time else "TBD",
            "location": ev.location,
            "capacity": ev.capacity,
            "mode": ev.mode
        }), 200
        
    except Exception as e:
        print(f"❌ Get event error: {str(e)}")
        return jsonify({"message": str(e)}), 500

@app.route("/add-event", methods=["POST"])
def add_event():
    try:
        data = request.get_json()
        
        # Convert string dates/times to Python objects
        date_obj = datetime.strptime(data['event_date'], '%Y-%m-%d').date()
        start_obj = datetime.strptime(data['start_time'], '%H:%M').time()
        end_obj = datetime.strptime(data['end_time'], '%H:%M').time()

        new_event = Event(
            created_by=data.get('created_by'),
            title=data['title'],
            mode=data['mode'],
            location=data['location'],
            event_date=date_obj,
            start_time=start_obj,
            end_time=end_obj,
            capacity=int(data['capacity']),
            description=data['description']
        )

        db.session.add(new_event)
        db.session.commit()
        
        print(f"✅ Event added: {data['title']}")
        return jsonify({"message": "Event created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"❌ Add event error: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

# --- JOB ROUTES ---

@app.route("/add-job", methods=["POST"])
def add_job():
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('role') or not data.get('company_name'):
            return jsonify({"message": "Role and Company Name are required"}), 400

        new_job = Job(
            role=data['role'],
            company_name=data['company_name'],
            location=data['location'],
            paid_status=data['paid_status'],
            duration=data['duration'],
            posted_by=data.get('posted_by')
        )

        db.session.add(new_job)
        db.session.commit()
        print(f"✅ New job posted: {data['role']} at {data['company_name']}")
        return jsonify({"message": "Job posted successfully"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"❌ Add job error: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/get-all-jobs", methods=["GET"])
def get_all_jobs():
    try:
        jobs = Job.query.order_by(Job.created_at.desc()).all()
        output = []
        
        for job in jobs:
            logo_letter = job.company_name[0].upper() if job.company_name else "J"
            
            output.append({
                "id": job.id,
                "role": job.role,
                "company": job.company_name,
                "location": job.location,
                "paid_status": job.paid_status,
                "duration": job.duration,
                "logo_letter": logo_letter
            })
        return jsonify(output), 200
        
    except Exception as e:
        print(f"❌ Get jobs error: {str(e)}")
        return jsonify({"message": str(e)}), 500

# --- USER ROUTES ---

@app.route('/get-all-users', methods=['GET'])
def get_all_users():
    try:
        users = User.query.all()
        
        user_list = []
        for user in users:
            user_list.append({
                "username": user.username,
                "email": user.email,
                "role": user.role.lower() if user.role else "student"
            })

        # Sort by role (Alumni first)
        user_list.sort(key=lambda x: x['role'] != 'alumni')

        return jsonify(user_list[:10])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- CHAT ROUTES ---

@app.route("/chat-users/<int:current_user_id>", methods=["GET"])
def get_chat_users(current_user_id):
    """Fetches all unique users who have message history with the logged-in user"""
    try:
        sent_ids = db.session.query(Message.receiver_id).filter(Message.sender_id == current_user_id).all()
        received_ids = db.session.query(Message.sender_id).filter(Message.receiver_id == current_user_id).all()

        history_ids = {id_tuple[0] for id_tuple in sent_ids} | {id_tuple[0] for id_tuple in received_ids}

        if current_user_id in history_ids:
            history_ids.remove(current_user_id)

        if not history_ids:
            return jsonify([]), 200

        chat_partners = User.query.filter(User.id.in_(history_ids)).all()

        return jsonify([{
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "dept": u.department
        } for u in chat_partners]), 200

    except Exception as e:
        print(f"❌ Sidebar Error: {str(e)}")
        return jsonify({"message": "Failed to load chat history"}), 500

@app.route("/send-message", methods=["POST"])
def send_message():
    """Save a new message"""
    try:
        data = request.get_json()
        
        new_msg = Message(
            sender_id=data['sender'],
            receiver_id=data['receiver'],
            content=data['content']
        )
        
        db.session.add(new_msg)
        db.session.commit()
        
        print(f"✅ Message sent: User {data['sender']} → User {data['receiver']}")
        return jsonify({"ok": True}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Send message error: {str(e)}")
        return jsonify({"message": str(e)}), 500

@app.route("/get-messages/<int:u1>/<int:u2>", methods=["GET"])
def get_messages(u1, u2):
    """Get chat history between two users"""
    try:
        msgs = Message.query.filter(
            ((Message.sender_id == u1) & (Message.receiver_id == u2)) |
            ((Message.sender_id == u2) & (Message.receiver_id == u1))
        ).order_by(Message.timestamp.asc()).all()
        
        return jsonify([{
            "sender": m.sender_id,
            "content": m.content,
            "time": m.timestamp.strftime("%H:%M")
        } for m in msgs]), 200
        
    except Exception as e:
        print(f"❌ Get messages error: {str(e)}")
        return jsonify({"message": str(e)}), 500

@app.route("/search-users", methods=["GET"])
def search_users():
    query = request.args.get('q', '')
    current_id = request.args.get('me', type=int)
    
    if not query:
        return jsonify([])

    users = User.query.filter(
        User.username.ilike(f"%{query}%"),
        User.id != current_id
    ).all()
    
    return jsonify([{
        "id": u.id,
        "username": u.username,
        "role": u.role,
        "dept": u.department
    } for u in users]), 200

# --- TEST SETUP ROUTE ---

@app.route("/setup-test")
def setup_test():
    """Generates test users and sample events"""
    try:
        # Create test users if they don't exist
        user_a = User.query.filter_by(email="test1@example.com").first()
        if not user_a:
            user_a = User(
                username="Alumni_User",
                email="test1@example.com",
                password_hash=bcrypt.generate_password_hash("123").decode('utf-8'),
                role="alumni",
                department="CS"
            )
            db.session.add(user_a)
        
        user_b = User.query.filter_by(email="test2@example.com").first()
        if not user_b:
            user_b = User(
                username="Student_User",
                email="test2@example.com",
                password_hash=bcrypt.generate_password_hash("123").decode('utf-8'),
                role="student",
                department="IT"
            )
            db.session.add(user_b)
        
        db.session.commit()

        # Create sample message
        existing_msg = Message.query.filter_by(sender_id=user_a.id, receiver_id=user_b.id).first()
        if not existing_msg:
            init_msg = Message(
                sender_id=user_a.id,
                receiver_id=user_b.id,
                content="Hello! This is our chat history."
            )
            db.session.add(init_msg)
        
        # Create sample events for testing calendar
        sample_events = [
            {
                "title": "Tech Career Workshop",
                "date": "2026-02-15",
                "mode": "Workshop",
                "location": "Main Hall",
                "time": "14:00"
            },
            {
                "title": "Alumni Networking Event",
                "date": "2026-02-20",
                "mode": "Networking",
                "location": "Campus Center",
                "time": "18:00"
            },
            {
                "title": "Coding Bootcamp",
                "date": "2026-02-25",
                "mode": "Training",
                "location": "Lab 101",
                "time": "10:00"
            }
        ]
        
        for ev_data in sample_events:
            existing_event = Event.query.filter_by(title=ev_data['title']).first()
            if not existing_event:
                date_obj = datetime.strptime(ev_data['date'], '%Y-%m-%d').date()
                start_obj = datetime.strptime(ev_data['time'], '%H:%M').time()
                end_obj = datetime.strptime('17:00', '%H:%M').time()
                
                new_event = Event(
                    created_by=user_a.id,
                    title=ev_data['title'],
                    mode=ev_data['mode'],
                    location=ev_data['location'],
                    event_date=date_obj,
                    start_time=start_obj,
                    end_time=end_obj,
                    capacity=50,
                    description=f"Sample event: {ev_data['title']}"
                )
                db.session.add(new_event)
        
        db.session.commit()

        return f"✅ Test setup complete! Users created (IDs: {user_a.id}, {user_b.id}) and sample events added."
    except Exception as e:
        db.session.rollback()
        return f"❌ Error: {str(e)}"

# --- MAIN ---

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        db.session.commit()
        print("="*60)
        print("🚀 Alumni Network Backend Server")
        print("="*60)
        print(f"📍 Server running on: http://127.0.0.1:5000")
        print(f"📊 Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"📅 Calendar API: http://127.0.0.1:5000/api/events")
        print(f"🧪 Test setup: http://127.0.0.1:5000/setup-test")
        print("="*60 + "\n")
    
    app.run(debug=True, port=5000)