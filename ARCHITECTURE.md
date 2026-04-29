# System Architecture

## 🏗️ Application Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
│                      (Browser)                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP Requests
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   FRONTEND                                   │
│              (React + Vite + TypeScript)                     │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Landing   │  │    Login    │  │   Signup    │         │
│  │    Page     │  │    Page     │  │    Page     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Dashboard  │  │  Students   │  │   Classes   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                               │
│  Port: 5173                                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ API Calls (axios)
                         │ http://localhost:8000/api/v1
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    BACKEND                                   │
│              (FastAPI + Python)                              │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              API Routes                              │   │
│  │                                                       │   │
│  │  /api/v1/auth/signup    - Create user               │   │
│  │  /api/v1/auth/login     - Login user                │   │
│  │  /api/v1/auth/me        - Get current user          │   │
│  │  /api/v1/students       - Student management        │   │
│  │  /api/v1/classes        - Class management          │   │
│  │  /api/v1/sessions       - Session management        │   │
│  │  /api/v1/attendance     - Attendance tracking       │   │
│  │  /api/v1/ai             - Face recognition          │   │
│  │  /api/v1/reports        - Generate reports          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  Port: 8000                                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ SQL Queries
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   DATABASE                                   │
│                  (PostgreSQL)                                │
│                                                               │
│  Tables:                                                     │
│  - users                                                     │
│  - students                                                  │
│  - classes                                                   │
│  - sessions                                                  │
│  - attendance_records                                        │
│                                                               │
│  Port: 5432                                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flow

### Signup Flow

```
1. User fills signup form
   └─> frontend/src/pages/Signup.tsx

2. Form submits
   └─> frontend/src/services/api.ts
       └─> POST http://localhost:8000/api/v1/auth/signup

3. Backend receives request
   └─> backend/main.py (CORS middleware)
       └─> backend/app/api/routers/auth.py
           └─> @router.post("/signup")

4. Backend validates data
   └─> Check if email exists
   └─> Check if username exists
   └─> Hash password

5. Backend saves to database
   └─> backend/app/crud.py
       └─> INSERT INTO users

6. Backend returns response
   └─> 201 Created + user data

7. Frontend receives response
   └─> Show success message
   └─> Redirect to login page
```

### Login Flow

```
1. User fills login form
   └─> frontend/src/pages/Login.tsx

2. Form submits
   └─> POST http://localhost:8000/api/v1/auth/login
       └─> Content-Type: application/x-www-form-urlencoded
       └─> username=xxx&password=xxx

3. Backend validates credentials
   └─> Find user by username/email
   └─> Verify password hash
   └─> Generate JWT token

4. Backend returns token
   └─> { "access_token": "xxx", "token_type": "bearer" }

5. Frontend stores token
   └─> localStorage.setItem('token', token)
   └─> Update AuthContext
   └─> Redirect to dashboard
```

### Protected Route Access

```
1. User navigates to /dashboard
   └─> frontend/src/App.tsx
       └─> <ProtectedRoute>

2. Check if token exists
   └─> const { token } = useAuth()
   └─> if (!token) redirect to /login

3. Make API request
   └─> axios interceptor adds token
       └─> Authorization: Bearer <token>

4. Backend validates token
   └─> backend/app/api/deps.py
       └─> get_current_user()
       └─> Decode JWT
       └─> Find user in database

5. Return protected data
   └─> If valid: return data
   └─> If invalid: 401 Unauthorized
```

---

## 📁 Project Structure

```
smart-attendance/
│
├── frontend/                    # React Frontend
│   ├── src/
│   │   ├── components/         # Reusable components
│   │   │   ├── ui/            # UI components (Button, Card, Input)
│   │   │   ├── Layout.tsx
│   │   │   ├── Navbar.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── contexts/          # React contexts
│   │   │   └── AuthContext.tsx
│   │   ├── pages/             # Page components
│   │   │   ├── Landing.tsx    # 🆕 Landing page
│   │   │   ├── Login.tsx      # 🆕 Modern login
│   │   │   ├── Signup.tsx     # 🆕 Modern signup
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Students.tsx
│   │   │   └── ...
│   │   ├── services/          # API services
│   │   │   └── api.ts         # Axios instance
│   │   ├── App.tsx            # Main app component
│   │   ├── main.tsx           # Entry point
│   │   └── index.css          # Global styles
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                     # FastAPI Backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── routers/       # API routes
│   │   │   │   ├── auth.py    # Authentication
│   │   │   │   ├── students.py
│   │   │   │   ├── classes.py
│   │   │   │   └── ...
│   │   │   └── deps.py        # Dependencies
│   │   ├── core/              # Core functionality
│   │   │   ├── config.py      # Configuration
│   │   │   ├── database.py    # Database connection
│   │   │   └── security.py    # Password hashing, JWT
│   │   ├── ai/                # AI/ML models
│   │   │   ├── face_recognizer.py
│   │   │   └── ...
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── schemas.py         # Pydantic schemas
│   │   └── crud.py            # Database operations
│   ├── migrations/            # Alembic migrations
│   ├── main.py                # FastAPI app
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
│
├── start-backend.bat           # 🆕 Backend startup script
├── start-frontend.bat          # 🆕 Frontend startup script
├── QUICK_FIX.md               # 🆕 Quick troubleshooting
├── BACKEND_STARTUP_GUIDE.md   # 🆕 Backend setup guide
├── TROUBLESHOOTING.md         # 🆕 Common issues
└── README.md                  # Project documentation
```

---

## 🔐 Authentication Flow

```
┌─────────────┐
│   Signup    │
└──────┬──────┘
       │
       │ 1. Submit form
       ▼
┌─────────────────────┐
│  POST /auth/signup  │
│  - username         │
│  - email            │
│  - password         │
│  - role             │
└──────┬──────────────┘
       │
       │ 2. Validate & hash password
       ▼
┌─────────────────────┐
│  Save to Database   │
└──────┬──────────────┘
       │
       │ 3. Return user data
       ▼
┌─────────────────────┐
│  Redirect to Login  │
└─────────────────────┘

┌─────────────┐
│    Login    │
└──────┬──────┘
       │
       │ 1. Submit credentials
       ▼
┌─────────────────────┐
│  POST /auth/login   │
│  - username         │
│  - password         │
└──────┬──────────────┘
       │
       │ 2. Verify credentials
       ▼
┌─────────────────────┐
│  Generate JWT Token │
└──────┬──────────────┘
       │
       │ 3. Return token
       ▼
┌─────────────────────┐
│ Store in localStorage│
└──────┬──────────────┘
       │
       │ 4. Redirect to Dashboard
       ▼
┌─────────────────────┐
│    Dashboard        │
└─────────────────────┘

Every API Request:
┌─────────────────────┐
│  Add Authorization  │
│  Header:            │
│  Bearer <token>     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Backend validates  │
│  token & returns    │
│  user data          │
└─────────────────────┘
```

---

## 🌐 Network Communication

### Development Setup

```
┌──────────────────────────────────────────────────────────┐
│  Your Computer                                            │
│                                                            │
│  ┌─────────────────┐         ┌─────────────────┐        │
│  │   Frontend      │         │    Backend      │        │
│  │   localhost:5173│◄───────►│ localhost:8000  │        │
│  │   (Vite)        │  HTTP   │   (Uvicorn)     │        │
│  └─────────────────┘         └────────┬────────┘        │
│                                        │                  │
│                                        │ SQL              │
│                                        ▼                  │
│                               ┌─────────────────┐        │
│                               │   PostgreSQL    │        │
│                               │ localhost:5432  │        │
│                               └─────────────────┘        │
└──────────────────────────────────────────────────────────┘
```

### API Endpoints

```
Base URL: http://localhost:8000/api/v1

Authentication:
├── POST   /auth/signup          Create new user
├── POST   /auth/login           Login and get token
└── GET    /auth/me              Get current user info

Students: (requires auth)
├── GET    /students             List all students
├── POST   /students             Create student
├── GET    /students/{id}        Get student by ID
├── PUT    /students/{id}        Update student
└── DELETE /students/{id}        Delete student

Classes: (requires auth)
├── GET    /classes              List all classes
├── POST   /classes              Create class
├── GET    /classes/{id}         Get class by ID
├── PUT    /classes/{id}         Update class
└── DELETE /classes/{id}         Delete class

Sessions: (requires auth)
├── GET    /sessions             List all sessions
├── POST   /sessions             Create session
├── GET    /sessions/{id}        Get session by ID
└── PUT    /sessions/{id}/end    End session

Attendance: (requires auth)
├── GET    /attendance           List attendance records
├── POST   /attendance           Mark attendance
└── GET    /attendance/session/{id}  Get session attendance

AI: (requires auth)
├── POST   /ai/recognize         Recognize face
└── POST   /ai/train             Train model

Reports: (requires auth)
├── GET    /reports/export       Export attendance data
└── GET    /reports/stats        Get statistics
```

---

## 🔧 Technology Stack

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **State Management**: React Context API

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.8+
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose)
- **Password Hashing**: Passlib (bcrypt)
- **Server**: Uvicorn

### AI/ML
- **Face Detection**: YOLO v8
- **Face Recognition**: FaceNet (PyTorch)
- **Computer Vision**: OpenCV
- **Deep Learning**: PyTorch

---

## 📊 Data Flow

### Student Registration & Attendance

```
1. Register Student
   ├─> Upload photo
   ├─> Extract face features (FaceNet)
   ├─> Store in database
   └─> Save face encoding

2. Start Attendance Session
   ├─> Create session record
   ├─> Activate camera
   └─> Load student face encodings

3. Capture & Recognize
   ├─> Detect faces (YOLO)
   ├─> Extract features (FaceNet)
   ├─> Compare with database
   ├─> Identify student
   └─> Mark attendance

4. Generate Report
   ├─> Query attendance records
   ├─> Calculate statistics
   ├─> Export to CSV/Excel/PDF
   └─> Display charts
```

---

## 🚀 Deployment Architecture

### Production Setup (Example)

```
┌─────────────────────────────────────────────────────────┐
│                    Internet                              │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  Load Balancer / CDN                     │
│                  (Cloudflare / AWS)                      │
└────────────┬────────────────────────┬────────────────────┘
             │                        │
             │ Frontend               │ Backend
             ▼                        ▼
┌─────────────────────┐   ┌─────────────────────┐
│   Static Hosting    │   │   API Server        │
│   (Vercel/Netlify)  │   │   (AWS EC2/Docker)  │
│   React Build       │   │   FastAPI + Uvicorn │
└─────────────────────┘   └──────────┬──────────┘
                                     │
                                     │ SQL
                                     ▼
                          ┌─────────────────────┐
                          │   Database          │
                          │   (AWS RDS/         │
                          │    PostgreSQL)      │
                          └─────────────────────┘
```

---

## 💡 Key Concepts

### CORS (Cross-Origin Resource Sharing)
- Frontend (port 5173) and Backend (port 8000) are different origins
- Backend must explicitly allow frontend origin
- Configured in `backend/main.py`

### JWT (JSON Web Tokens)
- Used for authentication
- Token contains user info (email, role)
- Sent in Authorization header: `Bearer <token>`
- Validated on every protected route

### Protected Routes
- Routes that require authentication
- Check for valid token before rendering
- Redirect to login if not authenticated

### State Management
- AuthContext provides auth state globally
- Token stored in localStorage
- User info available throughout app

---

**This architecture ensures a secure, scalable, and maintainable application! 🏗️**
