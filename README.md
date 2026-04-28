# Smart Face Attendance System 📸🏫

A professional, full-stack, AI-powered application that automates student attendance tracking using advanced facial recognition.

## 🚀 Overview
The Smart Face Attendance System eliminates the need for manual roll calls. It uses a live camera feed to detect student faces in real-time, matches them against a pre-registered database of face encodings, and automatically logs their attendance status. The platform includes a rich dashboard for administrators and teachers to view analytical data, manage student records, and export tailored attendance reports.

## 🏗️ Project Architecture
The application leverages a clean, resilient decoupled architecture:
1. **Frontend Client**: A modern Single Page Application (SPA) built with React and Vite. It heavily utilizes Tailwind CSS for styling and Recharts for live attendance trend visualizations.
2. **FastAPI Core**: A high-performance Python ASync API routing system. It interfaces with the database, issues JWT security tokens, enforces Role-Based Access Control (Admin vs. Teacher), and serves data payloads.
3. **AI Processing Module**: Runs seamlessly alongside the core API. Uses YOLOv8 for high-speed face detection and FaceNet for embedding vectorization. Matches real-time captured encodings to PostgreSQL profiles through cosine similarity tracking.
4. **Relational Database**: Powered by PostgreSQL to store \users\, \students\, \classes\, \sessions\, \ace_images\, and \ttendance_logs\.

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
1. **Detection Phase**: \live_camera.py\ captures frames using OpenCV. YOLOv8 scans the frame for localized face bounding boxes.
2. **Extraction Phase**: The detected face is cropped and normalized.
3. **Encoding Phase**: The normalized face tensor is passed into \InceptionResnetV1\ (FaceNet), which outputs a standard dense vector mapping the face features.
4. **Matching Phase**: The new vector is compared against all authorized student embeddings loaded from the database using mathematically optimized Euclidean distance/Cosine similarity. If the confidence exceeds the threshold (\> 0.8\), an \AttendanceLog\ is created in real-time.

## 💻 Installation & Setup

### Option A: Running Locally (Native)

**1. Clone the repository**

**2. Setup the Backend**
\\\ash
cd backend
python -m venv venv
# Activate venv: \env\Scripts\activate\ (Windows) or \source venv/bin/activate\ (Mac/Linux)
pip install -r requirements.txt
\\\
*Note: Ensure you have a running PostgreSQL database. Update the \DATABASE_URL\ in \pp/core/database.py\ if not using the default local instance.*

Start the FastAPI server:
\\\ash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
\\\

Start the AI Live Camera Feed (In a separate terminal):
\\\ash
cd backend
# Make sure the virtual environment is activated
python -m app.ai.live_camera
\\\

**3. Setup the Frontend**
\\\ash
cd frontend
npm install
npm run dev
\\\

### Option B: Docker Deployment (Recommended for Production)
Ensure Docker and Docker Compose are installed on your system.
\\\ash
docker-compose up --build -d
\\\
The application will launch the PostgreSQL Database, compile the Python FastAPI backend, build the Vite React application, and serve it via Nginx.
- **Frontend Dashboard**: \http://localhost:80\
- **Backend API**: \http://localhost:8000\

## 📊 Usage Guide
1. **Login**: Access the web portal. (Default accounts are configurable via the database).
2. **Dashboard**: Navigate to the home dashboard to view today's breakdown (Pie Chart), weekly trends (Area Chart), and monthly comparisons (Bar Chart).
3. **Manage Students**: Add students and map their Class/Course identifiers.
4. **AI Attendance**: Initialize the live camera script. When a registered student walks into the frame, their attendance profile will update automatically to \Present\.
5. **Exporting Reports**: Navigate to the *Attendance* tab to download exact filtered PDFs and Excel spreadsheets.

## 🔒 Security
- Passwords are salt-hashed using \crypt\.
- Full end-to-end endpoint projection using Bearer \JWT\.
- Role-based separation ensures Teachers read records, while Admins possess total CRUD command.

---
*Created for Smart Face Attendance System.*
