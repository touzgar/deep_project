# Smart Face Attendance System 📸🏫

A professional, full-stack, AI-powered application that automates student attendance tracking using advanced facial recognition.

## 🚀 Overview
The Smart Face Attendance System eliminates the need for manual roll calls. It uses a live camera feed to detect student faces in real-time, matches them against a pre-registered database of face encodings, and automatically logs their attendance status. The platform includes a rich dashboard for administrators and teachers to view analytical data, manage student records, and export tailored attendance reports.

## 🏗️ Project Architecture
The application leverages a clean, resilient decoupled architecture:
1. **Frontend Client**: A modern Single Page Application (SPA) built with React and Vite. It heavily utilizes Tailwind CSS for styling and Recharts for live attendance trend visualizations.
2. **FastAPI Core**: A high-performance Python ASync API routing system. It interfaces with the database, issues JWT security tokens, enforces Role-Based Access Control (Admin vs. Teacher), and serves data payloads.
3. **AI Processing Module**: Runs seamlessly alongside the core API. Uses YOLOv8 for high-speed face detection and FaceNet for embedding vectorization. Matches real-time captured encodings to PostgreSQL profiles through cosine similarity tracking.
4. **Relational Database**: Powered by PostgreSQL to store users, students, classes, sessions, face_images, and attendance_logs.

## 🛠️ Technologies
**Frontend:**
- React 18, Vite, TypeScript
- Tailwind CSS
- React Router DOM, Recharts, Lucide-React

**Backend:**
- FastAPI, Uvicorn
- SQLAlchemy, Pydantic, PostgreSQL (psycopg2)
- python-jose (JWT), passlib (bcrypt)
- Pandas, OpenPyXL, FPDF2 (Reporting & Exports)

**Artificial Intelligence (AI):**
- **Ultralytics YOLOv8**: For rapid, lightweight face/human detection.
- **FaceNet (facenet-pytorch)**: Generates 512-dimensional facial embeddings for extreme recognition accuracy.
- **OpenCV**: Connects to the local web-camera and renders bounding boxes natively.

**DevOps:**
- Docker, Docker Compose, Nginx

## 🧠 AI Model Integration
1. **Detection Phase**: live_camera.py captures frames using OpenCV. YOLOv8 scans the frame for localized face bounding boxes.
2. **Extraction Phase**: The detected face is cropped and normalized.
3. **Encoding Phase**: The normalized face tensor is passed into InceptionResnetV1 (FaceNet), which outputs a standard dense vector mapping the face features.
4. **Matching Phase**: The new vector is compared against all authorized student embeddings loaded from the database using mathematically optimized Euclidean distance/Cosine similarity. If the confidence exceeds the threshold (> 0.8), an AttendanceLog is created in real-time.

## 💻 Installation & Setup

### Prerequisites
- Python 3.9+ with pip
- Node.js 16+ with npm
- PostgreSQL 12+ database server
- Git

### Option A: Running Locally (Native)

**1. Clone the repository**
```bash
git clone <repository-url>
cd smart-face-attendance-system
```

**2. Setup PostgreSQL Database**
```bash
# Create a new PostgreSQL database
createdb attendance_db

# Or using psql:
psql -U postgres
CREATE DATABASE attendance_db;
\q
```

**3. Setup the Backend**
```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure database connection
# Edit backend/app/core/database.py or set environment variable:
# DATABASE_URL=postgresql://username:password@localhost:5432/attendance_db

# Run database migrations
alembic upgrade head

# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

**4. Setup the Frontend**
```bash
# Open a new terminal
cd frontend

# Install dependencies
npm install

# Configure API URL (optional - defaults to http://localhost:8000)
# Create frontend/.env file:
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

**5. Create Initial User Account**
```bash
# Option 1: Use the signup page at http://localhost:5173/signup

# Option 2: Use Python script to create admin user
cd backend
python -c "
from app.core.database import SessionLocal
from app import crud, schemas
db = SessionLocal()
user = schemas.UserCreate(
    username='admin',
    email='admin@example.com',
    password='admin123',
    role='admin'
)
crud.create_user(db, user)
db.close()
print('Admin user created!')
"
```

**6. Add Students and Face Images**
1. Login to the system at `http://localhost:5173/login`
2. Navigate to "Students" page
3. Click "Add Student" to create student records
4. Click "Manage Photos" for each student to upload face images
5. The AI module will automatically generate face embeddings

**7. Start Live Camera Attendance (Optional)**
```bash
# In a new terminal, with backend venv activated
cd backend
python -m app.ai.live_camera
```

This starts the live camera feed for real-time face recognition attendance.

### Option B: Docker Deployment (Recommended for Production)

Ensure Docker and Docker Compose are installed on your system.

```bash
# Build and start all services
docker-compose up --build -d
```

The application will launch:
- **PostgreSQL Database**: Internal container
- **Backend API**: `http://localhost:8000`
- **Frontend Dashboard**: `http://localhost:80`
- **Nginx Reverse Proxy**: Serves frontend and proxies API requests

**Access the Application:**
- Frontend: `http://localhost`
- Backend API Docs: `http://localhost:8000/docs`

**View Logs:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Stop Services:**
```bash
docker-compose down
```

### Environment Variables

**Backend (.env or environment):**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/attendance_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Frontend (.env):**
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

## 📊 Usage Guide

### 1. Authentication
- **Login**: Navigate to `http://localhost:5173/login` and enter your credentials
- **Signup**: Create a new account at `http://localhost:5173/signup` (choose role: Teacher or Admin)
- **Logout**: Click the logout button in the navigation bar

### 2. Dashboard
The dashboard displays real-time attendance analytics:
- **Stat Cards**: Total students, classes, sessions today, present/absent counts, attendance percentage
- **Weekly Attendance Chart**: Bar chart showing present/absent counts for the last 7 days
- **Monthly Rate Chart**: Line chart showing attendance percentage trends for the last 4 weeks
- **Today's Overview**: Pie chart showing present vs absent breakdown for today

All data is calculated in real-time from the PostgreSQL database.

### 3. Student Management
- **Add Students**: Click "Add Student" button, fill in details (Student ID, Name, Email, Class)
- **Edit Students**: Click the edit icon next to any student
- **Delete Students**: Click the delete icon (this will also delete all face images)
- **Manage Face Photos**: Click "Manage Photos" to upload multiple face images for AI recognition

### 4. Class Management
- Create and manage classes
- Assign students to classes
- View class rosters

### 5. Session Management
- Create attendance sessions for specific classes
- Set session times and status (scheduled, active, completed)
- Link sessions to teachers

### 6. Live Camera Attendance
- Click "Start Attendance" to activate webcam
- System automatically detects and recognizes student faces
- Attendance is logged in real-time to the database
- View recognized students in the sidebar with confidence scores
- Click "Stop Attendance" when done

### 7. Attendance History
- View all attendance records with student names
- Filter by class
- Export to CSV format
- Records show: Student name, Date, Time, Status

### 8. Reports
- Generate detailed attendance reports with filters
- Export to Excel or PDF format
- Filter by: Class, Session, Date Range, Status, Student
- View summary statistics

## 🔒 Security
- **Password Hashing**: All passwords are salt-hashed using bcrypt
- **JWT Authentication**: Full end-to-end endpoint protection using Bearer JWT tokens
- **Role-Based Access Control**: Teachers can read records, Admins have full CRUD permissions
- **Protected Routes**: Frontend routes require valid authentication tokens
- **Secure API**: All API endpoints (except auth) require valid JWT tokens

## 🧪 Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## 📝 API Documentation
Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

Key endpoints:
- `POST /api/v1/auth/signup` - Create new user account
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info
- `GET /api/v1/dashboard/stats` - Get dashboard statistics
- `GET /api/v1/students/` - List all students
- `POST /api/v1/students/` - Create new student
- `POST /api/v1/students/{id}/face-images` - Upload face images
- `GET /api/v1/attendance/` - List attendance records
- `POST /api/v1/ai/recognize` - Recognize face from image
- `GET /api/v1/reports/attendance` - Get attendance report

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
pg_isready

# Verify database exists
psql -U postgres -l | grep attendance_db

# Check connection string in backend/app/core/database.py
```

### Frontend Can't Connect to Backend
```bash
# Verify backend is running on port 8000
curl http://localhost:8000

# Check VITE_API_URL in frontend/.env
cat frontend/.env
```

### AI Module Issues
```bash
# Install required AI dependencies
pip install torch torchvision ultralytics facenet-pytorch opencv-python

# Download YOLOv8 model (should happen automatically)
# Model will be downloaded to backend/yolov8n.pt
```

### Permission Errors
```bash
# Ensure proper file permissions
chmod +x setup.sh
chmod -R 755 backend/uploads
```

## 📦 Project Structure
```
smart-face-attendance-system/
├── backend/
│   ├── app/
│   │   ├── ai/              # AI modules (face recognition, YOLOv8)
│   │   ├── api/             # API routers and dependencies
│   │   ├── core/            # Core config, database, security
│   │   ├── services/        # External services (UploadThing)
│   │   ├── utils/           # Utility functions
│   │   ├── crud.py          # Database CRUD operations
│   │   ├── models.py        # SQLAlchemy models
│   │   └── schemas.py       # Pydantic schemas
│   ├── migrations/          # Alembic database migrations
│   ├── uploads/             # Uploaded face images
│   ├── main.py              # FastAPI application entry point
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable React components
│   │   ├── contexts/        # React contexts (Auth)
│   │   ├── pages/           # Page components
│   │   ├── services/        # API service layer
│   │   └── App.tsx          # Main React component
│   ├── package.json         # Node dependencies
│   └── vite.config.ts       # Vite configuration
├── docker-compose.yml       # Docker orchestration
└── README.md               # This file
```

## 🤝 Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License
This project is licensed under the MIT License.

## 👥 Authors
Created for Smart Face Attendance System.

## 🙏 Acknowledgments
- YOLOv8 by Ultralytics
- FaceNet by David Sandberg
- FastAPI framework
- React and Vite communities

---
*For support or questions, please open an issue on GitHub.*
