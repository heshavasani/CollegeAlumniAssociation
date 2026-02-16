import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sapp import app, db, User, Message, bcrypt
from datetime import datetime

def create_test_users():
    with app.app_context():
        try:
            print("👥 Creating test users...\n")
            
            # User 1: Alice (Alumni)
            alice = User.query.filter_by(username="Alice_Alumni").first()
            if not alice:
                alice = User(
                    username="Alice_Alumni",
                    email="alice@alumni.com",
                    password_hash=bcrypt.generate_password_hash("password123").decode('utf-8'),
                    role="alumni",
                    department="Computer Science",
                    batch_year=2020
                )
                db.session.add(alice)
                db.session.flush()  # Get ID before commit
                print(f"✅ Created: Alice_Alumni (Alumni, CS 2020)")
            else:
                print(f"ℹ️  Alice_Alumni already exists (ID: {alice.id})")
            
            # User 2: Bob (Student)
            bob = User.query.filter_by(username="Bob_Student").first()
            if not bob:
                bob = User(
                    username="Bob_Student",
                    email="bob@student.com",
                    password_hash=bcrypt.generate_password_hash("password123").decode('utf-8'),
                    role="student",
                    department="Information Technology",
                    batch_year=2024
                )
                db.session.add(bob)
                db.session.flush()
                print(f"✅ Created: Bob_Student (Student, IT 2024)")
            else:
                print(f"ℹ️  Bob_Student already exists (ID: {bob.id})")
            
            # User 3: Carol (Alumni)
            carol = User.query.filter_by(username="Carol_Alumni").first()
            if not carol:
                carol = User(
                    username="Carol_Alumni",
                    email="carol@alumni.com",
                    password_hash=bcrypt.generate_password_hash("password123").decode('utf-8'),
                    role="alumni",
                    department="Electronics",
                    batch_year=2018
                )
                db.session.add(carol)
                db.session.flush()
                print(f"✅ Created: Carol_Alumni (Alumni, ECE 2018)")
            else:
                print(f"ℹ️  Carol_Alumni already exists (ID: {carol.id})")
            
            db.session.commit()
            
            # Create initial messages so users appear in each other's chat
            print("\n💬 Creating initial chat messages...\n")
            
            # Alice → Bob
            msg1 = Message.query.filter_by(sender_id=alice.id, receiver_id=bob.id).first()
            if not msg1:
                msg1 = Message(
                    sender_id=alice.id,
                    receiver_id=bob.id,
                    content="Hey Bob! Welcome to the alumni network! 👋"
                )
                db.session.add(msg1)
                print(f"✅ Alice → Bob: Welcome message")
            
            # Bob → Alice
            msg2 = Message.query.filter_by(sender_id=bob.id, receiver_id=alice.id).first()
            if not msg2:
                msg2 = Message(
                    sender_id=bob.id,
                    receiver_id=alice.id,
                    content="Thanks Alice! Happy to be here! 😊"
                )
                db.session.add(msg2)
                print(f"✅ Bob → Alice: Reply message")
            
            # Carol → Bob
            msg3 = Message.query.filter_by(sender_id=carol.id, receiver_id=bob.id).first()
            if not msg3:
                msg3 = Message(
                    sender_id=carol.id,
                    receiver_id=bob.id,
                    content="Hi Bob! Let me know if you need any career advice."
                )
                db.session.add(msg3)
                print(f"✅ Carol → Bob: Mentoring message")
            
            db.session.commit()
            
            print("\n" + "="*60)
            print("🎉 TEST USERS CREATED SUCCESSFULLY!")
            print("="*60)
            
            print("\n🔑 Login Credentials:")
            print("-" * 60)
            print(f"Username: Alice_Alumni  | Password: password123 | Role: Alumni")
            print(f"Username: Bob_Student   | Password: password123 | Role: Student")
            print(f"Username: Carol_Alumni  | Password: password123 | Role: Alumni")
            print("-" * 60)
            
            print("\n📱 Test Chat:")
            print("   1. Login as Bob_Student")
            print("   2. Go to Messages page")
            print("   3. You'll see Alice and Carol in contacts")
            print("   4. Click to chat with them!")
            
            print("\n🚀 Next Steps:")
            print("   1. Start Flask: python app.py")
            print("   2. Open browser: http://127.0.0.1:5000")
            print("   3. Go to login.html and use credentials above")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error creating test users: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    create_test_users()
