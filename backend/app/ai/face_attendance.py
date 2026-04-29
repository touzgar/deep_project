"""
Comprehensive AI Module for Face Attendance System
Features:
- YOLOv8 for face detection
- FaceNet for face embeddings
- OpenCV for image processing
- Save student face images
- Generate embeddings
- Compare embeddings using cosine similarity
- Confidence threshold
- Unknown face detection
"""

import cv2
import numpy as np
import torch
import base64
import os
import json
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from PIL import Image
import logging

# ML Libraries
from ultralytics import YOLO
from facenet_pytorch import InceptionResnetV1, MTCNN
from sklearn.metrics.pairwise import cosine_similarity

# Database
from sqlalchemy.orm import Session
from app import models
from app.core.database import get_db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceAttendanceAI:
    """
    Main AI class for face attendance system
    """
    
    def __init__(self, 
                 yolo_model_path: str = "yolov8n.pt",
                 confidence_threshold: float = 0.7,
                 face_size: int = 160,
                 device: str = None):
        """
        Initialize the AI system
        
        Args:
            yolo_model_path: Path to YOLO model
            confidence_threshold: Minimum confidence for face recognition
            face_size: Size to resize faces for FaceNet
            device: Device to use (cuda/cpu)
        """
        self.confidence_threshold = confidence_threshold
        self.face_size = face_size
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize models
        self._load_models(yolo_model_path)
        
        # Create directories
        self.face_images_dir = Path("uploads/face_images")
        self.face_images_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"FaceAttendanceAI initialized on {self.device}")
    
    def _load_models(self, yolo_model_path: str):
        """Load YOLO and FaceNet models"""
        try:
            # Load YOLO for face detection
            self.yolo_model = YOLO(yolo_model_path)
            logger.info("YOLO model loaded successfully")
            
            # Load FaceNet for embeddings
            self.facenet_model = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
            logger.info("FaceNet model loaded successfully")
            
            # Load MTCNN for face alignment (optional, better quality)
            self.mtcnn = MTCNN(
                image_size=self.face_size,
                margin=0,
                min_face_size=20,
                thresholds=[0.6, 0.7, 0.7],
                factor=0.709,
                post_process=True,
                device=self.device
            )
            logger.info("MTCNN model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def detect_faces_yolo(self, image: np.ndarray) -> List[Dict]:
        """
        Detect faces using YOLO
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of detected faces with bounding boxes and confidence
        """
        try:
            results = self.yolo_model(image, verbose=False)
            faces = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get coordinates and confidence
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = box.conf[0].cpu().numpy()
                        
                        # Filter by confidence and size
                        if conf > 0.5 and (x2 - x1) > 30 and (y2 - y1) > 30:
                            faces.append({
                                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                                'confidence': float(conf)
                            })
            
            return faces
            
        except Exception as e:
            logger.error(f"Error in YOLO face detection: {e}")
            return []
    
    def detect_faces_mtcnn(self, image: np.ndarray) -> List[Dict]:
        """
        Detect faces using MTCNN (more accurate but slower)
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of detected faces with bounding boxes and confidence
        """
        try:
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            # Detect faces
            boxes, probs = self.mtcnn.detect(pil_image)
            faces = []
            
            if boxes is not None:
                for box, prob in zip(boxes, probs):
                    if prob > 0.9:  # High confidence threshold for MTCNN
                        x1, y1, x2, y2 = box
                        faces.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': float(prob)
                        })
            
            return faces
            
        except Exception as e:
            logger.error(f"Error in MTCNN face detection: {e}")
            return []
    
    def extract_face_embedding(self, image: np.ndarray, bbox: List[int]) -> Optional[np.ndarray]:
        """
        Extract face embedding using FaceNet
        
        Args:
            image: Input image
            bbox: Bounding box [x1, y1, x2, y2]
            
        Returns:
            512-dimensional face embedding or None
        """
        try:
            x1, y1, x2, y2 = bbox
            
            # Validate bbox
            h, w = image.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            if x2 <= x1 or y2 <= y1:
                return None
            
            # Extract face region
            face = image[y1:y2, x1:x2]
            
            # Convert BGR to RGB
            face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            
            # Resize to required size
            face_resized = cv2.resize(face_rgb, (self.face_size, self.face_size))
            
            # Convert to PIL Image
            pil_face = Image.fromarray(face_resized)
            
            # Use MTCNN for preprocessing (alignment and normalization)
            face_tensor = self.mtcnn(pil_face)
            
            if face_tensor is None:
                # Fallback: manual preprocessing
                face_array = np.array(pil_face).astype(np.float32)
                face_array = (face_array - 127.5) / 128.0  # Normalize to [-1, 1]
                face_tensor = torch.tensor(face_array).permute(2, 0, 1).unsqueeze(0)
            else:
                face_tensor = face_tensor.unsqueeze(0)
            
            # Move to device
            face_tensor = face_tensor.to(self.device)
            
            # Generate embedding
            with torch.no_grad():
                embedding = self.facenet_model(face_tensor)
                embedding = embedding.cpu().numpy().flatten()
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error extracting face embedding: {e}")
            return None
    
    def save_student_face_image(self, 
                               student_id: int, 
                               image: np.ndarray, 
                               db: Session) -> Dict[str, Any]:
        """
        Save student face image and generate embedding
        
        Args:
            student_id: Student ID
            image: Face image
            db: Database session
            
        Returns:
            Result dictionary with success status and details
        """
        try:
            # Detect faces in the image
            faces = self.detect_faces_yolo(image)
            
            if not faces:
                return {
                    'success': False,
                    'message': 'No face detected in the image'
                }
            
            # Use the largest face (highest confidence)
            best_face = max(faces, key=lambda x: x['confidence'])
            
            # Extract embedding
            embedding = self.extract_face_embedding(image, best_face['bbox'])
            
            if embedding is None:
                return {
                    'success': False,
                    'message': 'Failed to extract face embedding'
                }
            
            # Save image file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"student_{student_id}_{timestamp}.jpg"
            image_path = self.face_images_dir / filename
            
            cv2.imwrite(str(image_path), image)
            
            # Save to database
            face_image = models.FaceImage(
                student_id=student_id,
                image_path=str(image_path),
                embedding_vector=embedding.tolist()  # Convert to list for JSON storage
            )
            
            db.add(face_image)
            db.commit()
            db.refresh(face_image)
            
            return {
                'success': True,
                'message': 'Face image saved successfully',
                'face_image_id': face_image.id,
                'embedding_size': len(embedding),
                'confidence': best_face['confidence']
            }
            
        except Exception as e:
            logger.error(f"Error saving student face image: {e}")
            db.rollback()
            return {
                'success': False,
                'message': f'Error saving face image: {str(e)}'
            }
    
    def compare_embeddings(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compare two face embeddings using cosine similarity
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity score (0-1, higher is more similar)
        """
        try:
            # Reshape for sklearn
            emb1 = embedding1.reshape(1, -1)
            emb2 = embedding2.reshape(1, -1)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(emb1, emb2)[0][0]
            
            # Convert to 0-1 range (cosine similarity is -1 to 1)
            similarity = (similarity + 1) / 2
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error comparing embeddings: {e}")
            return 0.0
    
    def recognize_face(self, image: np.ndarray, db: Session) -> Dict[str, Any]:
        """
        Recognize face in image against database
        
        Args:
            image: Input image
            db: Database session
            
        Returns:
            Recognition result with student info and confidence
        """
        try:
            # Detect faces
            faces = self.detect_faces_yolo(image)
            
            if not faces:
                return {
                    'success': False,
                    'message': 'No face detected',
                    'recognized': False
                }
            
            # Use the best face
            best_face = max(faces, key=lambda x: x['confidence'])
            
            # Extract embedding
            query_embedding = self.extract_face_embedding(image, best_face['bbox'])
            
            if query_embedding is None:
                return {
                    'success': False,
                    'message': 'Failed to extract face embedding',
                    'recognized': False
                }
            
            # Get all stored embeddings from database
            stored_faces = db.query(models.FaceImage).filter(
                models.FaceImage.embedding_vector.isnot(None)
            ).all()
            
            if not stored_faces:
                return {
                    'success': True,
                    'message': 'No registered faces in database',
                    'recognized': False,
                    'is_unknown': True
                }
            
            # Find best match
            best_match = None
            best_similarity = 0.0
            
            for stored_face in stored_faces:
                try:
                    # Convert stored embedding back to numpy array
                    stored_embedding = np.array(stored_face.embedding_vector)
                    
                    # Compare embeddings
                    similarity = self.compare_embeddings(query_embedding, stored_embedding)
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = stored_face
                        
                except Exception as e:
                    logger.error(f"Error comparing with stored face {stored_face.id}: {e}")
                    continue
            
            # Check if similarity meets threshold
            if best_similarity >= self.confidence_threshold:
                student = best_match.student
                return {
                    'success': True,
                    'recognized': True,
                    'student_id': student.id,
                    'student_name': f"{student.first_name} {student.last_name}",
                    'confidence': best_similarity,
                    'face_detection_confidence': best_face['confidence'],
                    'message': 'Face recognized successfully'
                }
            else:
                return {
                    'success': True,
                    'recognized': False,
                    'is_unknown': True,
                    'confidence': best_similarity,
                    'face_detection_confidence': best_face['confidence'],
                    'message': f'Unknown face (similarity: {best_similarity:.3f}, threshold: {self.confidence_threshold})'
                }
                
        except Exception as e:
            logger.error(f"Error in face recognition: {e}")
            return {
                'success': False,
                'message': f'Recognition error: {str(e)}',
                'recognized': False
            }
    
    def process_base64_image(self, base64_string: str) -> Optional[np.ndarray]:
        """
        Convert base64 string to OpenCV image
        
        Args:
            base64_string: Base64 encoded image
            
        Returns:
            OpenCV image or None
        """
        try:
            # Decode base64
            image_data = base64.b64decode(base64_string)
            
            # Convert to numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            
            # Decode image
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return image
            
        except Exception as e:
            logger.error(f"Error processing base64 image: {e}")
            return None
    
    def get_student_embeddings_count(self, db: Session) -> Dict[str, int]:
        """
        Get count of embeddings per student
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with student counts
        """
        try:
            # Count embeddings per student
            result = db.query(
                models.Student.id,
                models.Student.first_name,
                models.Student.last_name,
                db.func.count(models.FaceImage.id).label('embedding_count')
            ).outerjoin(models.FaceImage).group_by(
                models.Student.id,
                models.Student.first_name,
                models.Student.last_name
            ).all()
            
            return {
                'total_students': len(result),
                'students_with_embeddings': len([r for r in result if r.embedding_count > 0]),
                'total_embeddings': sum(r.embedding_count for r in result),
                'details': [
                    {
                        'student_id': r.id,
                        'name': f"{r.first_name} {r.last_name}",
                        'embedding_count': r.embedding_count
                    }
                    for r in result
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting embedding counts: {e}")
            return {'error': str(e)}
    
    def update_confidence_threshold(self, new_threshold: float):
        """
        Update confidence threshold
        
        Args:
            new_threshold: New threshold value (0.0 to 1.0)
        """
        if 0.0 <= new_threshold <= 1.0:
            self.confidence_threshold = new_threshold
            logger.info(f"Confidence threshold updated to {new_threshold}")
        else:
            raise ValueError("Threshold must be between 0.0 and 1.0")
    
    def cleanup_old_images(self, db: Session, days_old: int = 30):
        """
        Clean up old face images
        
        Args:
            db: Database session
            days_old: Remove images older than this many days
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Find old images in database
            old_images = db.query(models.FaceImage).filter(
                models.FaceImage.created_at < cutoff_date
            ).all()
            
            removed_count = 0
            for image in old_images:
                try:
                    # Remove file
                    if os.path.exists(image.image_path):
                        os.remove(image.image_path)
                    
                    # Remove database record
                    db.delete(image)
                    removed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error removing image {image.id}: {e}")
            
            db.commit()
            logger.info(f"Cleaned up {removed_count} old face images")
            
        except Exception as e:
            logger.error(f"Error in cleanup: {e}")
            db.rollback()

# Global instance
face_ai = None

def get_face_ai() -> FaceAttendanceAI:
    """Get global FaceAttendanceAI instance"""
    global face_ai
    if face_ai is None:
        face_ai = FaceAttendanceAI()
    return face_ai