"""
Database Checker - Use this to debug database issues
Run this anytime to see what's in your database
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Message, Event, Job, Skill

def check_database():
    """Check the current state of the database"""
    with app.app_context():
        try:
            print("\n" + "="*70)
            print("DATABASE STATUS CHECK")
            print("="*70)
            
            # Check Users
            print("\n👥 USERS TABLE:")
            print("-" * 70)
            users = User.query.all()
            if users:
                for u in users:
                    print(f"   ID: {u.id:3d} | {u.username:20s} | Role: {u.role:8s} | {u.department}")
            else:
                print("   ⚠️  No users found!")
            print(f"\n   Total Users: {len(users)}")
            
            # Check Messages
            print("\n💬 MESSAGES TABLE:")
            print("-" * 70)
            messages = Message.query.all()
            if messages:
                for m in messages:
                    sender = User.query.get(m.sender_id)
                    receiver = User.query.get(m.receiver_id)
                    sender_name = sender.username if sender else "Unknown"
                    receiver_name = receiver.username if receiver else "Unknown"
                    preview = m.content[:40] + "..." if len(m.content) > 40 else m.content
                    print(f"   {sender_name} → {receiver_name}: {preview}")
            else:
                print("   ℹ️  No messages found")
            print(f"\n   Total Messages: {len(messages)}")
            
            # Check Events
            print("\n📅 EVENTS TABLE:")
            print("-" * 70)
            events = Event.query.all()
            if events:
                for e in events:
                    print(f"   ID: {e.id:3d} | {e.title[:40]:40s} | {e.event_date}")
            else:
                print("   ℹ️  No events found")
            print(f"\n   Total Events: {len(events)}")
            
            # Check Jobs
            print("\n💼 JOBS TABLE:")
            print("-" * 70)
            jobs = Job.query.all()
            if jobs:
                for j in jobs:
                    print(f"   ID: {j.id:3d} | {j.role:30s} | {j.company_name}")
            else:
                print("   ℹ️  No jobs found")
            print(f"\n   Total Jobs: {len(jobs)}")
            
            # Check Skills
            print("\n⭐ SKILLS TABLE:")
            print("-" * 70)
            skills = Skill.query.all()
            if skills:
                skill_count = {}
                for s in skills:
                    user = User.query.get(s.user_id)
                    username = user.username if user else "Unknown"
                    if username not in skill_count:
                        skill_count[username] = []
                    if s.skill_name:
                        skill_count[username].append(s.skill_name)
                
                for username, user_skills in skill_count.items():
                    skills_str = ", ".join(user_skills) if user_skills else "No skills"
                    print(f"   {username}: {skills_str}")
            else:
                print("   ℹ️  No skills found")
            print(f"\n   Total Skill Entries: {len(skills)}")
            
            print("\n" + "="*70)
            print("✅ Database check complete!")
            print("="*70 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error checking database: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_database()
