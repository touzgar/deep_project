#!/bin/bash

echo "🔧 FIXING CORS ISSUE"
echo "===================="
echo ""

echo "📋 Problem: Backend container has old code without proper CORS"
echo "📋 Solution: Rebuild backend with updated CORS configuration"
echo ""

# Stop backend
echo "🛑 Step 1: Stopping backend container..."
docker-compose stop backend

# Remove old container and image
echo "🗑️  Step 2: Removing old backend container and image..."
docker rm attendance_backend 2>/dev/null || true
docker rmi deep_project-backend 2>/dev/null || true

# Rebuild backend
echo "🔨 Step 3: Rebuilding backend with updated CORS..."
docker-compose build --no-cache backend

if [ $? -ne 0 ]; then
    echo "❌ Build failed! Check the error above."
    exit 1
fi

# Start backend
echo "🚀 Step 4: Starting backend..."
docker-compose up -d backend

# Wait for backend to start
echo "⏳ Step 5: Waiting for backend to start (15 seconds)..."
sleep 15

# Test backend
echo "✅ Step 6: Testing backend..."
curl http://localhost:8000

echo ""
echo ""
echo "🎉 DONE! Backend has been rebuilt with proper CORS configuration"
echo ""
echo "📋 Now test your application:"
echo "   1. Open http://localhost:5173"
echo "   2. Try to login"
echo "   3. Check browser console (F12) - should see NO CORS errors"
echo ""
echo "📊 Check backend logs:"
echo "   docker logs attendance_backend --tail 50"
echo ""
