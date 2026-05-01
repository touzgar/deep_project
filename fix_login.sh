#!/bin/bash

echo "🔧 FIXING LOGIN ISSUE"
echo "===================="
echo ""

echo "📋 Problem: Bcrypt password hashing error"
echo "📋 Solution: Delete all users and recreate with fixed hashing"
echo ""

# Step 1: Delete all users from database
echo "🗑️  Step 1: Deleting all existing users..."
docker exec attendance_backend python -c "
import sys
sys.path.insert(0, '/app')
from app.core.database import SessionLocal
from app import models

db = SessionLocal()
try:
    deleted = db.query(models.User).delete()
    db.commit()
    print(f'Deleted {deleted} users')
except Exception as e:
    print(f'Error: {e}')
    db.rollback()
finally:
    db.close()
"

# Step 2: Create new admin user
echo "👤 Step 2: Creating new admin user..."
docker exec attendance_backend python -c "
import sys
sys.path.insert(0, '/app')
from app.core.database import SessionLocal
from app import models
from app.core.security import get_password_hash

db = SessionLocal()
try:
    admin = models.User(
        username='admin',
        email='admin@test.com',
        password_hash=get_password_hash('admin123'),
        role='admin'
    )
    db.add(admin)
    db.commit()
    print('✅ Admin user created')
    print('   Username: admin')
    print('   Password: admin123')
except Exception as e:
    print(f'Error: {e}')
    db.rollback()
finally:
    db.close()
"

# Step 3: Test login
echo ""
echo "🧪 Step 3: Testing login..."
response=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123")

if [[ $response == *"access_token"* ]]; then
    echo "✅ Login works!"
else
    echo "❌ Login failed: $response"
fi

echo ""
echo "===================="
echo "🎉 FIX COMPLETE!"
echo ""
echo "📋 Now test in browser:"
echo "   1. Open: http://localhost:5173/login"
echo "   2. Username: admin"
echo "   3. Password: admin123"
echo "   4. Click 'Sign In'"
echo ""
echo "✅ Login should work now!"
echo ""
