import cv2
import json
import time
from datetime import datetime, timedelta
from app.ai.face_recognizer import SmartFaceRecognizer
from app.core import database
from app import models

# Load AI Engine
face_ai = SmartFaceRecognizer(threshold=0.65) # Adjusted for cosine distance tolerances

def fetch_known_faces(db):
    """
    Fetches the latest face embeddings from PostgreSQL and constructs a live memory map.
    Returns: {"student_id": [embedding values], ...}
    """
    known_db = {}
    # Retrieve all face embeddings
    face_data = db.query(models.FaceImage).filter(models.FaceImage.embedding_vector != None).all()
    
    for face in face_data:
        student = face.student.student_id if face.student.student_id else str(face.student.id)
        if student not in known_db:
            known_db[student] = []
        # Get embedding vector (already a list from JSON column)
        try:
            emb = face.embedding_vector
            if isinstance(emb, str):
                emb = json.loads(emb)
            known_db[student].append(emb)
        except Exception as e:
            print(f"Error parsing embedding for {student}: {e}")
            pass
    return known_db

def get_or_create_active_session(db):
    """
    Retrieves the first active session or creates a generic one for logging purposes.
    """
    session = db.query(models.Session).filter(models.Session.status == "active").first()
    if not session:
        # Check if we have a generic class
        db_class = db.query(models.Class).first()
        if not db_class:
            db_class = models.Class(name="General Attendance", description="Default class for attendance")
            db.add(db_class)
            db.commit()
            db.refresh(db_class)
        
        # Get first teacher user
        teacher = db.query(models.User).filter(models.User.role.in_(["admin", "teacher"])).first()
        if not teacher:
            raise Exception("No teacher/admin user found. Please create a user first.")
            
        session = models.Session(
            class_id=db_class.id,
            teacher_id=teacher.id,
            title="Live Camera Session",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + timedelta(hours=8),
            status="active"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    return session

def log_recent_attendance(db, student_str_id, session_id, match_accuracy, confidence_score):
    """
    Logs attendance if the student hasn't been logged in the last 5 minutes.
    """
    student = db.query(models.Student).filter(models.Student.student_id == student_str_id).first()
    if not student:
        # Try by ID if student_id is numeric
        try:
            student = db.query(models.Student).filter(models.Student.id == int(student_str_id)).first()
        except:
            pass
    
    if not student:
        return False
        
    five_mins_ago = datetime.utcnow() - timedelta(minutes=5)
    recent_log = db.query(models.AttendanceLog).filter(
        models.AttendanceLog.student_id == student.id,
        models.AttendanceLog.session_id == session_id,
        models.AttendanceLog.check_in_time >= five_mins_ago
    ).first()
    
    if not recent_log:
        new_log = models.AttendanceLog(
            student_id=student.id,
            session_id=session_id,
            status="Present",
            confidence=float(match_accuracy)
        )
        db.add(new_log)
        db.commit()
        return True
    return False

def run_live_recognition():
    """
    Launches PC's primary camera and performs continuous detection formatting boxes 
    and matching FaceNet data to existing PostgreSQL schemas.
    """
    db = next(database.get_db())
    known_faces = fetch_known_faces(db)
    active_session = get_or_create_active_session(db)
    
    print(f"Loaded {len(known_faces)} students into recognition memory.")
    print(f"Active Session ID: {active_session.id}")
    
    # 0 = default webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Camera could not be opened.")
        return

    print("Starting Live Smart Face Attendance Feed... Press 'q' to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. YOLOv8 locates all faces and extracts bounds
        faces = face_ai.detect_faces(frame)
        
        for face in faces:
            # 2. Extract boundary variables
            x1, y1, x2, y2 = face["box"]
            conf = face["confidence"]

            # 3. Generate high precision FaceNet 512-d embeddings via PyTorch
            embedding = face_ai.get_embedding(frame, face["box"])
            
            # 4. Compare embeddings with PostgreSQL data
            student_id = "Unknown"
            sim = 0.0
            color = (0, 0, 255)
            
            if embedding is not None and len(known_faces) > 0:
                student_id, sim = face_ai.identify_face(embedding, known_faces)
                
                if student_id != "Unknown":
                    # Successfully identified, log attendance
                    logged = log_recent_attendance(db, student_id, active_session.id, sim, conf)
                    if logged:
                        print(f"Attendance automatically recorded for: {student_id} (Accuracy: {sim:.2f})")
                        
                    label = f"{student_id} ({sim:.2f})"
                    color = (0, 255, 0)
                else:
                    label = f"Unknown ({sim:.2f})"
            else:
                label = f"Detecting... {conf:.2f}"
                color = (255, 200, 0)
            
            # 5. Visual Rendering formatting BGR frames
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, max(y1 - 10, 10)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.imshow("Smart Face Attendance System - Scanner", frame)
        
        # Standard graceful quit toggle
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_live_recognition()
