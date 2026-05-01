#!/usr/bin/env python3
"""
Reset all users in the database
This fixes the bcrypt password issue
"""

import sys
sys.path.insert(0, 'backend')

from app.core.database import SessionLocal, engine
from app import models
from app.core.security import get_password_hash

def reset_users():
    print("🔄 Resetting users...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Delete all existing users
        deleted = db.query(models.User).delete()
        db.commit()
        print(f"✅ Deleted {deleted} existing users")
        
        # Create a new admin user
        admin_user = models.User(
            username="admin",
            email="admin@test.com",
            password_hash=get_password_hash("admin123"),
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        print("✅ Created new admin user")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Role: admin")
        
        # Create a test teacher user
        teacher_user = models.User(
            username="teacher",
            email="teacher@test.com",
            password_hash=get_password_hash("teacher123"),
            role="teacher"
        )
        db.add(teacher_user)
        db.commit()
        print("✅ Created new teacher user")
        print("   Username: teacher")
        print("   Password: teacher123")
        print("   Role: teacher")
        
        print("\n🎉 Users reset successfully!")
        print("\n📋 You can now login with:")
        print("   Admin: admin / admin123")
        print("   Teacher: teacher / teacher123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_users()
