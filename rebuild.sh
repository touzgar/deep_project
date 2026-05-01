#!/bin/bash

echo "🛑 Stopping all containers..."
docker-compose down

echo "🗑️  Removing old images and build cache..."
docker rmi deep_project-frontend deep_project-backend attendance_frontend attendance_backend 2>/dev/null || true
docker builder prune -f

echo "🔨 Building new images with correct configuration..."
docker-compose build --no-cache --progress=plain

echo ""
echo "📦 Checking if build was successful..."
if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "🚀 Starting containers..."
    docker-compose up -d
    
    echo "⏳ Waiting for containers to start (30 seconds)..."
    sleep 30
    
    echo "✅ Checking container status..."
    docker ps
    
    echo ""
    echo "🎉 Done! Your application should now be available at:"
    echo "   Frontend: http://localhost:3001"
    echo "   Backend:  http://localhost:8000"
    echo ""
    echo "📋 To check logs:"
    echo "   docker logs attendance_frontend"
    echo "   docker logs attendance_backend"
else
    echo "❌ Build failed! Check the error messages above."
    echo ""
    echo "Common issues:"
    echo "1. Make sure Docker is running"
    echo "2. Check if you have enough disk space"
    echo "3. Try running: docker system prune -a"
    exit 1
fi
