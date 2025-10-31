"""
Video processor for facial landmark detection and frame processing.

This module handles webcam video capture, face detection, and facial
landmark extraction using OpenCV and dlib.
"""

import cv2
import dlib
import numpy as np
from typing import Optional, Tuple, Any
import streamlit as st
from imutils import face_utils
import threading
import time


class VideoProcessor:
    """Processes video frames for facial landmark detection."""
    
    def __init__(self):
        """Initialize the VideoProcessor."""
        self.face_detector = None
        self.landmark_predictor = None
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.current_landmarks = None
        self.frame_lock = threading.Lock()
        self.detection_confidence = 0.5
        
        # Initialize face detection models
        self._init_models()
    
    @st.cache_resource
    def _init_models(_self):
        """Initialize face detection and landmark prediction models."""
        try:
            # Initialize dlib face detector
            face_detector = dlib.get_frontal_face_detector()
            
            # Initialize dlib landmark predictor
            # Note: You need to download shape_predictor_68_face_landmarks.dat
            # from dlib's website or use a different predictor
            landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
            
            return face_detector, landmark_predictor
            
        except Exception as e:
            st.error(f"Error initializing face detection models: {str(e)}")
            st.info("Please download 'shape_predictor_68_face_landmarks.dat' from dlib's website")
            return None, None
    
    def initialize_camera(self, camera_index: int = 0) -> bool:
        """
        Initialize camera capture.
        
        Args:
            camera_index: Camera device index (default: 0)
            
        Returns:
            True if camera initialized successfully, False otherwise
        """
        try:
            # Release existing capture if any
            if self.cap is not None:
                self.cap.release()
            
            # Initialize video capture
            self.cap = cv2.VideoCapture(camera_index)
            
            if not self.cap.isOpened():
                return False
            
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Initialize models
            self.face_detector, self.landmark_predictor = self._init_models()
            
            return self.face_detector is not None and self.landmark_predictor is not None
            
        except Exception:
            return False
    
    def start_capture(self) -> None:
        """Start video capture in a separate thread."""
        if self.cap is None or not self.cap.isOpened():
            return
        
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
    
    def stop_capture(self) -> None:
        """Stop video capture."""
        self.is_running = False
        
        if hasattr(self, 'capture_thread') and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
    
    def _capture_loop(self) -> None:
        """Main capture loop (runs in separate thread)."""
        while self.is_running and self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            
            if ret:
                # Process the frame
                landmarks = self._detect_landmarks(frame)
                
                # Update current frame and landmarks thread-safely
                with self.frame_lock:
                    self.current_frame = frame.copy()
                    self.current_landmarks = landmarks
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.01)
    
    def get_current_frame_and_landmarks(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Get the current frame and detected landmarks.
        
        Returns:
            Tuple of (frame, landmarks) or (None, None) if not available
        """
        with self.frame_lock:
            if self.current_frame is not None:
                return self.current_frame.copy(), self.current_landmarks
            return None, None
    
    def _detect_landmarks(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Detect facial landmarks in a frame.
        
        Args:
            frame: Input video frame
            
        Returns:
            Numpy array of landmarks or None if no face detected
        """
        if self.face_detector is None or self.landmark_predictor is None:
            return None
        
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_detector(gray)
            
            if len(faces) == 0:
                return None
            
            # Use the largest face (first one returned by detector)
            face = faces[0]
            
            # Detect landmarks
            landmarks = self.landmark_predictor(gray, face)
            
            # Convert to numpy array
            landmarks_array = face_utils.shape_to_np(landmarks)
            
            return landmarks_array
            
        except Exception:
            return None
    
    def draw_landmarks(self, frame: np.ndarray, landmarks: np.ndarray) -> np.ndarray:
        """
        Draw facial landmarks on frame.
        
        Args:
            frame: Input frame
            landmarks: Facial landmarks array
            
        Returns:
            Frame with landmarks drawn
        """
        if landmarks is None:
            return frame
        
        output_frame = frame.copy()
        
        # Draw all landmarks
        for (x, y) in landmarks:
            cv2.circle(output_frame, (x, y), 1, (0, 255, 0), -1)
        
        # Draw eye contours
        left_eye = landmarks[36:42]
        right_eye = landmarks[42:48]
        
        cv2.drawContours(output_frame, [left_eye], -1, (0, 255, 255), 1)
        cv2.drawContours(output_frame, [right_eye], -1, (0, 255, 255), 1)
        
        return output_frame
    
    def capture_single_frame(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Capture a single frame and detect landmarks.
        
        Returns:
            Tuple of (frame, landmarks) or (None, None) if failed
        """
        if self.cap is None or not self.cap.isOpened():
            return None, None
        
        ret, frame = self.cap.read()
        if not ret:
            return None, None
        
        landmarks = self._detect_landmarks(frame)
        return frame, landmarks
    
    def get_frame_with_annotations(self, show_landmarks: bool = True, 
                                 show_face_box: bool = False) -> Optional[np.ndarray]:
        """
        Get current frame with optional annotations.
        
        Args:
            show_landmarks: Whether to show facial landmarks
            show_face_box: Whether to show face bounding box
            
        Returns:
            Annotated frame or None if not available
        """
        frame, landmarks = self.get_current_frame_and_landmarks()
        
        if frame is None:
            return None
        
        output_frame = frame.copy()
        
        if landmarks is not None:
            if show_landmarks:
                output_frame = self.draw_landmarks(output_frame, landmarks)
            
            if show_face_box:
                # Calculate face bounding box from landmarks
                x_coords = landmarks[:, 0]
                y_coords = landmarks[:, 1]
                
                x_min, x_max = int(np.min(x_coords)), int(np.max(x_coords))
                y_min, y_max = int(np.min(y_coords)), int(np.max(y_coords))
                
                # Add some padding
                padding = 20
                x_min = max(0, x_min - padding)
                y_min = max(0, y_min - padding)
                x_max = min(frame.shape[1], x_max + padding)
                y_max = min(frame.shape[0], y_max + padding)
                
                cv2.rectangle(output_frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
        
        return output_frame
    
    def is_camera_active(self) -> bool:
        """
        Check if camera is active and capturing.
        
        Returns:
            True if camera is active, False otherwise
        """
        return (self.cap is not None and 
                self.cap.isOpened() and 
                self.is_running)
    
    def get_camera_info(self) -> dict:
        """
        Get camera information and settings.
        
        Returns:
            Dictionary with camera information
        """
        if self.cap is None or not self.cap.isOpened():
            return {}
        
        return {
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': self.cap.get(cv2.CAP_PROP_FPS),
            'backend': self.cap.getBackendName()
        }
    
    def set_detection_confidence(self, confidence: float) -> None:
        """
        Set face detection confidence threshold.
        
        Args:
            confidence: Confidence threshold (0.0 to 1.0)
        """
        self.detection_confidence = max(0.0, min(1.0, confidence))
    
    def cleanup(self) -> None:
        """Clean up video processor resources."""
        self.stop_capture()
        
        with self.frame_lock:
            self.current_frame = None
            self.current_landmarks = None