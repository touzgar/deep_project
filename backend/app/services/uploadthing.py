"""
UploadThing integration service for file uploads
"""
import requests
import base64
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class UploadThingService:
    """Service for handling file uploads with UploadThing"""
    
    def __init__(self):
        # Load credentials from environment variables only (no defaults for security)
        self.api_key = os.getenv("UPLOADTHING_TOKEN")
        self.app_id = os.getenv("UPLOADTHING_APP_ID")
        self.secret = os.getenv("UPLOADTHING_SECRET")
        self.base_url = "https://api.uploadthing.com"
        
        # Log warning if credentials are not set
        if not all([self.api_key, self.app_id, self.secret]):
            logger.warning("UploadThing credentials not configured. File uploads will use local storage.")
        
    def upload_file(self, file_data: bytes, filename: str, content_type: str = "image/jpeg") -> Dict[str, Any]:
        """
        Upload file to UploadThing
        
        Args:
            file_data: File bytes
            filename: Name of the file
            content_type: MIME type
            
        Returns:
            Upload result with URL and metadata
        """
        try:
            # Prepare the upload request
            headers = {
                "Authorization": f"Bearer {self.secret}",
                "Content-Type": "application/json"
            }
            
            # Convert file to base64 for API
            file_b64 = base64.b64encode(file_data).decode('utf-8')
            
            payload = {
                "files": [{
                    "name": filename,
                    "type": content_type,
                    "data": file_b64
                }]
            }
            
            # Make upload request
            response = requests.post(
                f"{self.base_url}/api/upload",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "url": result.get("files", [{}])[0].get("url"),
                    "key": result.get("files", [{}])[0].get("key"),
                    "size": len(file_data),
                    "filename": filename
                }
            else:
                logger.error(f"UploadThing upload failed: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Upload failed: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error uploading to UploadThing: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_file(self, file_key: str) -> bool:
        """
        Delete file from UploadThing
        
        Args:
            file_key: File key to delete
            
        Returns:
            Success status
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.secret}",
                "Content-Type": "application/json"
            }
            
            response = requests.delete(
                f"{self.base_url}/api/deleteFile",
                json={"fileKey": file_key},
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error deleting from UploadThing: {e}")
            return False

# Global instance
uploadthing_service = UploadThingService()

def get_uploadthing_service() -> UploadThingService:
    """Get UploadThing service instance"""
    return uploadthing_service