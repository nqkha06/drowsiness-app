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


def ensure_directory_exists(directory_path: str) -> None:
    """
    Create directory if it doesn't exist.
    
    Args:
        directory_path: Path to the directory
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


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


def calculate_moving_average(values: List[float], window_size: int = 5) -> List[float]:
    """
    Calculate moving average of values.
    
    Args:
        values: List of numeric values
        window_size: Size of the moving window
        
    Returns:
        List of moving averages
    """
    if len(values) < window_size:
        return values
    
    moving_averages = []
    for i in range(len(values) - window_size + 1):
        window_avg = sum(values[i:i + window_size]) / window_size
        moving_averages.append(window_avg)
    
    # Pad the beginning with original values
    return values[:window_size-1] + moving_averages


def validate_ear_threshold(threshold: float) -> bool:
    """
    Validate EAR threshold value.
    
    Args:
        threshold: EAR threshold value
        
    Returns:
        True if valid, False otherwise
    """
    return 0.1 <= threshold <= 0.5


def get_alert_sound_path() -> str:
    """
    Get the path to the alert sound file.
    
    Returns:
        Path to alert sound file
    """
    # This would be the path to an actual sound file
    # For this implementation, we'll use a system beep
    return None