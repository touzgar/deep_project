#!/bin/bash

echo "🛑 Stopping backend container..."
docker-compose stop backend

echo "🗑️  Removing old backend image..."
docker rmi deep_project-backend 2>/dev/null || true

echo "🔨 Building backend image..."
docker-compose build --no-cache backend

if [ $? -eq 0 ]; then
    echo "✅ Backend build successful!"
    echo ""
    echo "🚀 Starting backend container..."
    docker-compose up -d backend
    
    echo "⏳ Waiting for backend to start (10 seconds)..."
    sleep 10
    
    echo "✅ Testing backend..."
    curl http://localhost:8000
    
    echo ""
    echo ""
    echo "🎉 Done! Backend is running at http://localhost:8000"
    echo ""
    echo "📋 Check logs with: docker logs attendance_backend"
else
    echo "❌ Backend build failed!"
    exit 1
fi
