from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key referring to the 'id' in the existing 'users' table 
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Storing the receiver's ID
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Username of the sender
    username = db.Column(db.String(100), nullable=False)
    
    # The actual message text
    content = db.Column(db.Text, nullable=False)
    
    # Timestamp for when the message was received/sent
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Optional: Relationship to easily fetch user objects if needed
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])