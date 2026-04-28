import React, { useState, useEffect, useRef } from 'react';
import { Play, StopCircle, RotateCcw, AlertTriangle } from 'lucide-react';
import api from '../services/api';

export default function LiveCamera() {
  const [isCapturing, setIsCapturing] = useState(false);
  const [detections, setDetections] = useState<any[]>([]);
  const [error, setError] = useState<string>('');
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Stop video stream when unmounting
  useEffect(() => {
    return () => {
      stopVideoStream();
    };
  }, []);

  // Set up frame capture interval
  useEffect(() => {
    let captureInterval: NodeJS.Timeout;
    
    if (isCapturing) {
      captureInterval = setInterval(() => {
        captureAndSendFrame();
      }, 1000); // 1 frame per second
    }

    return () => {
      if (captureInterval) clearInterval(captureInterval);
    };
  }, [isCapturing]);

  const startVideoStream = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 1280, height: 720 } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setError('');
      }
      return true;
    } catch (err: any) {
      console.error('Error accessing webcam:', err);
      setError('Could not access webcam. Please check permissions.');
      return false;
    }
  };

  const stopVideoStream = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
  };

  const captureAndSendFrame = async () => {
    if (!videoRef.current || !canvasRef.current) return;
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    if (video.readyState !== video.HAVE_ENOUGH_DATA) return;
    
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw current frame to canvas
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Get image as base64 data URL
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    
    try {
      // Send to backend
      const response = await api.post('/ai/recognize', {
        image: imageData.split(',')[1] // remove data:image/jpeg;base64, part
      });
      
      // Add valid detections to list (avoid duplicates)
      if (response.data && response.data.recognized) {
        setDetections(prev => {
          // Check if student already detected recently
          const existingIdx = prev.findIndex(d => d.student_id === response.data.student_id);
          if (existingIdx >= 0) {
            // Update time/confidence if better
            const newList = [...prev];
            if (response.data.confidence > newList[existingIdx].confidence) {
              newList[existingIdx].confidence = response.data.confidence;
            }
            newList[existingIdx].time = new Date().toLocaleTimeString();
            return newList;
          }
          
          // Add new detection
          return [{
            ...response.data,
            time: new Date().toLocaleTimeString()
          }, ...prev].slice(0, 50); // Keep last 50
        });
      }
    } catch (err) {
      console.error('Error recognizing face:', err);
    }
  };

  const startCapture = async () => {
    const success = await startVideoStream();
    if (success) {
      setIsCapturing(true);
      setDetections([]);
    }
  };

  const stopCapture = () => {
    setIsCapturing(false);
    stopVideoStream();
  };

  const resetDetections = () => {
    setDetections([]);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Live Camera Attendance</h1>
        <div className="flex gap-2">
          <button
            onClick={startCapture}
            disabled={isCapturing}
            className="bg-green-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-green-700 disabled:bg-gray-400"
          >
            <Play className="w-4 h-4"/> Start Attendance
          </button>
          <button
            onClick={stopCapture}
            disabled={!isCapturing}
            className="bg-red-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-red-700 disabled:bg-gray-400"
          >
            <StopCircle className="w-4 h-4"/> Stop Attendance
          </button>
          <button
            onClick={resetDetections}
            className="bg-gray-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-gray-700"
          >
            <RotateCcw className="w-4 h-4"/> Reset List
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-gray-900 rounded-lg overflow-hidden shadow-lg relative min-h-[400px] flex items-center justify-center">
            {/* Hidden canvas for capturing frames */}
            <canvas ref={canvasRef} className="hidden" />
            
            <video 
              ref={videoRef} 
              autoPlay 
              playsInline 
              muted 
              className={`w-full max-h-[600px] object-contain ${isCapturing ? 'block' : 'hidden'}`}
            />
            
            {!isCapturing && (
              <div className="text-center text-white absolute inset-0 flex flex-col items-center justify-center bg-gray-900 z-10">
                <div className="text-2xl font-bold mb-2">Camera Not Active</div>
                <p className="text-gray-400">Click "Start Attendance" to open webcam</p>
              </div>
            )}
            
            {isCapturing && (
              <div className="absolute top-4 right-4 bg-black bg-opacity-50 px-3 py-1 rounded-full flex items-center gap-2 z-20">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                <span className="text-white text-sm font-medium">LIVE</span>
              </div>
            )}
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-4 flex flex-col h-[400px] lg:h-auto">
          <h2 className="text-lg font-bold mb-4 border-b pb-2">Recognized Students</h2>
          <div className="flex-1 overflow-y-auto space-y-3 pr-2">
            {detections.length === 0 ? (
              <div className="h-full flex items-center justify-center text-gray-500 text-sm">
                Waiting for faces...
              </div>
            ) : (
              detections.map((detection: any, idx: number) => (
                <div key={`${detection.student_id}-${idx}`} className="border border-green-200 p-3 rounded-lg bg-green-50 shadow-sm transition-all duration-300 animate-in fade-in slide-in-from-top-2">
                  <div className="flex justify-between items-start mb-1">
                    <div className="font-bold text-gray-900">{detection.student_name}</div>
                    <span className="text-xs bg-green-200 text-green-800 px-2 py-1 rounded-full font-medium">
                      {detection.status || 'Present'}
                    </span>
                  </div>
                  <div className="flex justify-between items-end mt-2">
                    <div className="text-sm text-gray-600">ID: {detection.student_id}</div>
                    <div className="text-xs text-gray-500">{detection.time}</div>
                  </div>
                  <div className="mt-2 w-full bg-gray-200 rounded-full h-1.5">
                    <div 
                      className={`h-1.5 rounded-full ${detection.confidence > 0.85 ? 'bg-green-500' : 'bg-yellow-500'}`} 
                      style={{ width: `${Math.min(100, Math.max(0, detection.confidence * 100))}%` }}
                    ></div>
                  </div>
                  <div className="text-xs text-right mt-1 text-gray-500">
                    {(detection.confidence * 100).toFixed(1)}% match
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}