#!/bin/bash

echo "🔄 Changing frontend port from 3001 to 5173..."
echo ""

# Stop current frontend
echo "🛑 Stopping current frontend container..."
docker-compose stop frontend

# Remove old container
echo "🗑️  Removing old frontend container..."
docker rm attendance_frontend 2>/dev/null || true

# Start frontend with new port
echo "🚀 Starting frontend on port 5173..."
docker-compose up -d frontend

# Wait for it to start
echo "⏳ Waiting for frontend to start (10 seconds)..."
sleep 10

# Check status
echo "✅ Checking status..."
docker ps | grep frontend

echo ""
echo "🎉 Done! Frontend is now running on port 5173"
echo ""
echo "📋 Access your application at:"
echo "   http://localhost:5173"
echo ""
echo "⚠️  IMPORTANT: Stop any dev server (npm run dev) before accessing!"
echo ""
