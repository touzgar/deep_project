@echo off
echo 🛑 Stopping all containers...
docker-compose down

echo 🗑️  Removing old images...
docker rmi attendance_frontend attendance_backend 2>nul

echo 🔨 Building new images with correct configuration...
docker-compose build --no-cache

echo 🚀 Starting containers...
docker-compose up -d

echo ⏳ Waiting for containers to start (30 seconds)...
timeout /t 30 /nobreak >nul

echo ✅ Checking container status...
docker ps

echo.
echo 🎉 Done! Your application should now be available at:
echo    Frontend: http://localhost:3001
echo    Backend:  http://localhost:8000
echo.
echo 📋 To check logs:
echo    docker logs attendance_frontend
echo    docker logs attendance_backend
