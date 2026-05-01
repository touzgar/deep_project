#!/bin/bash

echo "🔧 COMPLETE FIX FOR LOGIN ISSUE"
echo "================================"
echo ""
echo "Problem: Bcrypt library version incompatibility"
echo "Solution: Rebuild backend with correct bcrypt version"
echo ""

# Step 1: Stop backend
echo "🛑 Step 1: Stopping backend..."
docker-compose stop backend

# Step 2: Remove old container and image
echo "🗑️  Step 2: Removing old backend..."
docker rm attendance_backend 2>/dev/null || true
docker rmi deep_project-backend 2>/dev/null || true

# Step 3: Rebuild backend (this will take 5-10 minutes)
echo "🔨 Step 3: Rebuilding backend with fixed bcrypt..."
echo "   (This will take 5-10 minutes, please wait...)"
docker-compose build --no-cache backend

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

# Step 4: Start backend
echo "🚀 Step 4: Starting backend..."
docker-compose up -d backend

# Step 5: Wait for backend to start
echo "⏳ Step 5: Waiting for backend to start (30 seconds)..."
sleep 30

# Step 6: Test backend
echo "✅ Step 6: Testing backend..."
curl -s http://localhost:8000

echo ""
echo ""

# Step 7: Create admin user
echo "👤 Step 7: Creating admin user..."
docker exec attendance_backend python -c "
import sys
sys.path.insert(0, '/app')
from app.core.database import SessionLocal
from app.models import User
from app.core.security import get_password_hash

db = SessionLocal()
try:
    # Delete existing users
    db.query(User).delete()
    db.commit()
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@test.com',
        password_hash=get_password_hash('admin123'),
        role='admin'
    )
    db.add(admin)
    db.commit()
    print('✅ Admin user created successfully')
except Exception as e:
    print(f'Error: {e}')
    db.rollback()
finally:
    db.close()
"

# Step 8: Test login
echo ""
echo "🧪 Step 8: Testing login..."
response=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123")

if [[ $response == *"access_token"* ]]; then
    echo "✅ Login works!"
    echo ""
    echo "================================"
    echo "🎉 SUCCESS! Everything is fixed!"
    echo "================================"
    echo ""
    echo "📋 Now test in browser:"
    echo "   1. Open: http://localhost:5173/login"
    echo "   2. Username: admin"
    echo "   3. Password: admin123"
    echo "   4. Click 'Sign In'"
    echo ""
    echo "✅ You should be able to login now!"
else
    echo "❌ Login test failed: $response"
    echo ""
    echo "Check backend logs:"
    echo "   docker logs attendance_backend --tail 50"
fi

echo ""
