#!/bin/bash

# Live Camera Attendance System - Setup Script
# This script sets up the entire system for development or production

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.8+ is required"
        exit 1
    fi
    
    # Check Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    else
        print_error "Node.js 16+ is required"
        exit 1
    fi
    
    # Check PostgreSQL
    if command_exists psql; then
        print_success "PostgreSQL client found"
    else
        print_warning "PostgreSQL client not found. Install with: sudo apt install postgresql-client"
    fi
    
    # Check Docker (optional)
    if command_exists docker; then
        print_success "Docker found"
        DOCKER_AVAILABLE=true
    else
        print_warning "Docker not found. Docker deployment will not be available."
        DOCKER_AVAILABLE=false
    fi
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Download YOLO model if not exists
    if [ ! -f "yolov8n.pt" ]; then
        print_status "Downloading YOLO model..."
        wget -O yolov8n.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
        print_success "YOLO model downloaded"
    else
        print_success "YOLO model already exists"
    fi
    
    # Create .env file if not exists
    if [ ! -f ".env" ]; then
        print_status "Creating backend .env file..."
        cat > .env << EOF
DATABASE_URL=postgresql://admin:adminpassword@localhost:5432/attendance_db
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ALGORITHM=HS256
EOF
        print_success "Backend .env file created"
    fi
    
    cd ..
}

# Function to setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Create .env file if not exists
    if [ ! -f ".env" ]; then
        print_status "Creating frontend .env file..."
        cat > .env << EOF
VITE_API_URL=http://localhost:8000/api/v1
EOF
        print_success "Frontend .env file created"
    fi
    
    cd ..
}

# Function to setup database
setup_database() {
    print_status "Setting up database..."
    
    # Check if PostgreSQL is running
    if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
        print_warning "PostgreSQL is not running on localhost:5432"
        print_status "You can either:"
        print_status "1. Start local PostgreSQL service"
        print_status "2. Use Docker: docker run -d --name postgres -p 5432:5432 -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=adminpassword -e POSTGRES_DB=attendance_db postgres:15-alpine"
        print_status "3. Use docker-compose: docker-compose up -d db"
        return
    fi
    
    cd backend
    source venv/bin/activate
    
    # Run migrations
    print_status "Running database migrations..."
    alembic upgrade head
    print_success "Database migrations completed"
    
    cd ..
}

# Function to run tests
run_tests() {
    print_status "Running system tests..."
    
    cd backend
    source venv/bin/activate
    cd ..
    
    python test_live_camera.py
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    # Start backend
    print_status "Starting backend server..."
    cd backend
    source venv/bin/activate
    nohup uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    cd ..
    
    # Wait for backend to start
    sleep 5
    
    # Start frontend
    print_status "Starting frontend server..."
    cd frontend
    nohup npm run dev -- --host 0.0.0.0 > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    cd ..
    
    print_success "Services started!"
    print_status "Backend: http://localhost:8000"
    print_status "Frontend: http://localhost:5173"
    print_status "Logs: backend.log, frontend.log"
    print_status "PIDs: backend.pid, frontend.pid"
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    
    if [ -f "backend.pid" ]; then
        kill $(cat backend.pid) 2>/dev/null || true
        rm backend.pid
        print_success "Backend stopped"
    fi
    
    if [ -f "frontend.pid" ]; then
        kill $(cat frontend.pid) 2>/dev/null || true
        rm frontend.pid
        print_success "Frontend stopped"
    fi
}

# Function to setup Docker
setup_docker() {
    if [ "$DOCKER_AVAILABLE" = false ]; then
        print_error "Docker is not available"
        return 1
    fi
    
    print_status "Setting up Docker environment..."
    
    # Ensure YOLO model exists
    if [ ! -f "backend/yolov8n.pt" ]; then
        print_status "Downloading YOLO model for Docker..."
        wget -O backend/yolov8n.pt https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
    fi
    
    # Build and start services
    print_status "Building and starting Docker services..."
    docker-compose up -d
    
    print_success "Docker services started!"
    print_status "Frontend: http://localhost:3000"
    print_status "Backend: http://localhost:8000"
    print_status "Database: localhost:5432"
}

# Function to show usage
show_usage() {
    echo "Live Camera Attendance System - Setup Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install     - Install all dependencies and setup system"
    echo "  start       - Start backend and frontend services"
    echo "  stop        - Stop running services"
    echo "  test        - Run system tests"
    echo "  docker      - Setup and start with Docker"
    echo "  docker-dev  - Setup and start with Docker (development mode)"
    echo "  clean       - Clean up temporary files and stop services"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install     # Full installation"
    echo "  $0 start       # Start services"
    echo "  $0 docker      # Use Docker"
}

# Main script logic
case "${1:-install}" in
    "install")
        print_status "Starting Live Camera Attendance System installation..."
        check_requirements
        setup_backend
        setup_frontend
        setup_database
        run_tests
        print_success "Installation completed!"
        print_status "Run '$0 start' to start the services"
        ;;
    
    "start")
        start_services
        ;;
    
    "stop")
        stop_services
        ;;
    
    "test")
        run_tests
        ;;
    
    "docker")
        check_requirements
        setup_docker
        ;;
    
    "docker-dev")
        check_requirements
        if [ "$DOCKER_AVAILABLE" = false ]; then
            print_error "Docker is not available"
            exit 1
        fi
        print_status "Starting Docker development environment..."
        docker-compose -f docker-compose.dev.yml up -d
        print_success "Docker development environment started!"
        print_status "Frontend: http://localhost:5173"
        print_status "Backend: http://localhost:8000"
        ;;
    
    "clean")
        print_status "Cleaning up..."
        stop_services
        rm -f backend.log frontend.log
        print_success "Cleanup completed"
        ;;
    
    "help"|"-h"|"--help")
        show_usage
        ;;
    
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac