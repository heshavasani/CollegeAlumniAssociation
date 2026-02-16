"""
Database Initialization Script
Run this FIRST to create all database tables
"""

import sys
import os

# Add current directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sapp import app, db, User, Skill, Event, Job, Message

def init_database():
    """Initialize the database with all tables"""
    with app.app_context():
        try:
            # Drop all existing tables (WARNING: Deletes all data)
            print("⚠️  Dropping existing tables...")
            db.drop_all()
            
            # Create all tables fresh
            print("📦 Creating new tables...")
            db.create_all()
            
            print("\n✅ Database initialized successfully!")
            print("\n📋 Tables created:")
            print("   ✓ users")
            print("   ✓ skills")
            print("   ✓ events")
            print("   ✓ jobs")
            print("   ✓ messages")
            
            print("\n🎯 Next steps:")
            print("   1. Run: python create_test_users.py")
            print("   2. Start Flask: python app.py")
            print("   3. Open browser: http://127.0.0.1:5000")
            
        except Exception as e:
            print(f"\n❌ Error initializing database: {e}")
            print("\nMake sure you have the correct app.py file!")
            sys.exit(1)

if __name__ == "__main__":
    init_database()
