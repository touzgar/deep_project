#!/bin/bash

# Start local development environment
# Usage: ./scripts/local-dev.sh

echo "Starting local development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Start services
docker-compose up -d db

echo "Waiting for database to be ready..."
sleep 5

# Start backend in development mode
cd backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

source venv/bin/activate || source venv/Scripts/activate
pip install -r requirements.txt

echo "Running database migrations..."
alembic upgrade head

echo "Starting backend on port 8000..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ../frontend

echo "Installing frontend dependencies..."
npm install

echo "Starting frontend on port 5173..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Development environment started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; docker-compose down; exit" INT
wait
