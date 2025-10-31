"""
Eye Aspect Ratio (EAR) calculator module.

This module implements the EAR calculation algorithm used to detect
eye closure and drowsiness based on facial landmarks.
"""

import numpy as np
from typing import List, Tuple
from .utils import euclidean_distance, get_eye_landmarks


class EARCalculator:
    """
    Calculator for Eye Aspect Ratio (EAR) based on facial landmarks.
    
    The EAR is calculated using the formula:
    EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
    
    Where p1, p2, p3, p4, p5, p6 are the 6 facial landmarks of an eye.
    """
    
    def __init__(self):
        self.ear_history = []
        self.max_history_length = 100
    
    def calculate_eye_ear(self, eye_landmarks: List[Tuple[int, int]]) -> float:
        """
        Calculate EAR for a single eye.
        
        Args:
            eye_landmarks: List of 6 (x, y) coordinates for eye landmarks
            
        Returns:
            EAR value as float
        """
        if len(eye_landmarks) != 6:
            raise ValueError("Eye landmarks must contain exactly 6 points")
        
        # Vertical eye landmarks
        # First vertical line (p2-p6)
        A = euclidean_distance(eye_landmarks[1], eye_landmarks[5])
        
        # Second vertical line (p3-p5) 
        B = euclidean_distance(eye_landmarks[2], eye_landmarks[4])
        
        # Horizontal eye landmark (p1-p4)
        C = euclidean_distance(eye_landmarks[0], eye_landmarks[3])
        
        # Calculate EAR
        ear = (A + B) / (2.0 * C)
        return ear
    
    def calculate_both_eyes_ear(self, landmarks: np.ndarray) -> Tuple[float, float, float]:
        """
        Calculate EAR for both eyes and return average.
        
        Args:
            landmarks: Facial landmarks array from dlib detector
            
        Returns:
            Tuple of (left_ear, right_ear, average_ear)
        """
        try:
            # Get left and right eye landmarks
            left_eye = get_eye_landmarks(landmarks, 'left')
            right_eye = get_eye_landmarks(landmarks, 'right')
            
            # Calculate EAR for each eye
            left_ear = self.calculate_eye_ear(left_eye)
            right_ear = self.calculate_eye_ear(right_eye)
            
            # Calculate average EAR
            average_ear = (left_ear + right_ear) / 2.0
            
            # Store in history
            self._update_history(average_ear)
            
            return left_ear, right_ear, average_ear
            
        except Exception as e:
            # Return default values if calculation fails
            return 0.0, 0.0, 0.0
    
    def _update_history(self, ear_value: float) -> None:
        """
        Update EAR history for trend analysis.
        
        Args:
            ear_value: Current EAR value
        """
        self.ear_history.append(ear_value)
        
        # Keep only recent history
        if len(self.ear_history) > self.max_history_length:
            self.ear_history = self.ear_history[-self.max_history_length:]
    
    def get_ear_history(self) -> List[float]:
        """
        Get the history of EAR values.
        
        Returns:
            List of recent EAR values
        """
        return self.ear_history.copy()
    
    def get_average_ear_trend(self, window_size: int = 10) -> float:
        """
        Get the average EAR over the last few frames.
        
        Args:
            window_size: Number of recent frames to average
            
        Returns:
            Average EAR over the specified window
        """
        if len(self.ear_history) == 0:
            return 0.0
        
        recent_values = self.ear_history[-window_size:]
        return sum(recent_values) / len(recent_values)
    
    def reset_history(self) -> None:
        """Reset the EAR history."""
        self.ear_history = []
    
    def is_ear_stable(self, threshold: float = 0.05, window_size: int = 5) -> bool:
        """
        Check if EAR values are stable (not fluctuating too much).
        
        Args:
            threshold: Maximum standard deviation for stability
            window_size: Number of recent frames to check
            
        Returns:
            True if EAR is stable, False otherwise
        """
        if len(self.ear_history) < window_size:
            return False
        
        recent_values = self.ear_history[-window_size:]
        std_dev = np.std(recent_values)
        
        return std_dev < threshold