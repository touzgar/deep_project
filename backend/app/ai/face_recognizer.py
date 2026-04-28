"""
AI Module for Smart Face Attendance System
Uses YOLOv8 for fast face detection.
Uses FaceNet (InceptionResnetV1) for high-accuracy standard 512-d embeddings.
"""
import cv2
import numpy as np
import torch
from ultralytics import YOLO
from facenet_pytorch import InceptionResnetV1
from PIL import Image

class SmartFaceRecognizer:
    def __init__(self, yolo_model_path="yolov8n-face.pt", threshold=0.7):
        """
        Initializes the ML Models.
        - YOLOv8 (nano) specifically trained on faces (or fallback to standard if missing, filtering 'person' class 0).
        - FaceNet PyTorch initialized with VGGFace2 pre-trained weights.
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load YOLOv8 face detector
        try:
            self.detector = YOLO(yolo_model_path)
            self.is_face_model = True
        except FileNotFoundError:
            # Fallback to standard YOLOv8 nano and detect 'person' (Class 0)
            self.detector = YOLO("yolov8n.pt")
            self.is_face_model = False

        # Load FaceNet model to the appropriate device
        self.encoder = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        self.recognition_threshold = threshold

    def detect_faces(self, frame):
        """
        Runs the YOLOv8 model to yield bounding boxes of all faces in the frame.
        """
        # If it's a standard model, filter for class 0 (person). If face model, accept default.
        classes = [0] if not self.is_face_model else None
        results = self.detector(frame, classes=classes, verbose=False)
        
        faces = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                conf = box.conf[0].item()
                # Ensure the box is reasonably sized
                if (x2 - x1) > 20 and (y2 - y1) > 20: 
                    faces.append({
                        "box": (int(x1), int(y1), int(x2), int(y2)),
                        "confidence": conf
                    })
        return faces

    def get_embedding(self, frame, box):
        """
        Crops the face from the frame using the YOLO box, processes it, and generates a FaceNet embedding.
        """
        x1, y1, x2, y2 = box
        # Validate boundaries
        h, w = frame.shape[:2]
        x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)
        
        face_img = frame[y1:y2, x1:x2]
        if face_img.size == 0:
            return None

        # Format for FaceNet (RGB, 160x160)
        face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(face_rgb).resize((160, 160))
        
        # Normalize to [-1, 1] bounds and convert to Tensor
        img_array = np.array(pil_img).astype(np.float32)
        img_array = (img_array - 127.5) / 128.0
        
        # (Channels, Height, Width) format required by PyTorch
        img_tensor = torch.tensor(img_array).permute(2, 0, 1).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            embedding = self.encoder(img_tensor).cpu().numpy()[0]
            
        return embedding

    def compare_embeddings(self, emb1, emb2):
        """
        Calculates cosine similarity between two embeddings.
        """
        dot_product = np.dot(emb1, emb2)
        norm_a = np.linalg.norm(emb1)
        norm_b = np.linalg.norm(emb2)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def identify_face(self, face_embedding, known_faces_db):
        """
        Checks the generated embedding against a dictionary of known encodings.
        `known_faces_db` format: { "student_id_1": [emb1, emb2], "student_id_2": [emb1] }
        """
        best_match = "Unknown"
        highest_sim = -1.0
        
        for student_id, encodings in known_faces_db.items():
            for known_emb in encodings:
                sim = self.compare_embeddings(face_embedding, np.array(known_emb))
                if sim > highest_sim:
                    highest_sim = sim
                    best_match = student_id
        
        if highest_sim >= self.recognition_threshold:
            return best_match, float(highest_sim)
        
        return "Unknown", float(highest_sim)
