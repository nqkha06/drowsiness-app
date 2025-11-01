"""
Utility functions for the drowsiness detection application.

This module contains helper functions for facial landmark processing,
file operations, and other common utilities.
"""

import numpy as np
from typing import List, Tuple
import os

# Define the eye landmark indices for dlib's 68-point predictor
LEFT_EYE_LANDMARKS = [36, 37, 38, 39, 40, 41]
RIGHT_EYE_LANDMARKS = [42, 43, 44, 45, 46, 47]


def get_eye_landmarks(landmarks: np.ndarray, eye_type: str) -> List[Tuple[int, int]]:
    """
    Extract eye landmarks coordinates.
    
    Args:
        landmarks: Numpy array of facial landmarks (68 points)
        eye_type: 'left' or 'right' eye
        
    Returns:
        List of (x, y) coordinates for the specified eye
    """
    if eye_type.lower() == 'left':
        indices = LEFT_EYE_LANDMARKS
    elif eye_type.lower() == 'right':
        indices = RIGHT_EYE_LANDMARKS
    else:
        raise ValueError("eye_type must be 'left' or 'right'")
    
    eye_points = []
    for i in indices:
        x = landmarks[i][0]
        y = landmarks[i][1]
        eye_points.append((x, y))
    
    return eye_points


def euclidean_distance(point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
    """
    Calculate euclidean distance between two points.
    
    Args:
        point1: First point (x, y)
        point2: Second point (x, y)
        
    Returns:
        Euclidean distance as float
    """
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def format_timestamp(timestamp: str) -> str:
    """
    Format timestamp for display.
    
    Args:
        timestamp: ISO format timestamp string
        
    Returns:
        Formatted timestamp string
    """
    from datetime import datetime
    dt = datetime.fromisoformat(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

