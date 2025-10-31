"""
Drowsiness detector with EAR threshold and frame counting logic.

This module implements the main drowsiness detection algorithm using
Eye Aspect Ratio (EAR) thresholds and consecutive frame counting.
"""

import time
from typing import Optional, Dict, List, Tuple
from .ear_calculator import EARCalculator
from .alert_service import AlertService
from .db_repository import AlertRepository


class DrowsinessDetector:
    """Main drowsiness detection class with EAR-based algorithm."""
    
    def __init__(self, 
                 ear_threshold: float = 0.25,
                 consecutive_frames_threshold: int = 20,
                 alert_cooldown: float = 5.0):
        """
        Initialize the DrowsinessDetector.
        
        Args:
            ear_threshold: EAR value below which drowsiness is detected
            consecutive_frames_threshold: Number of consecutive frames needed to trigger alert
            alert_cooldown: Minimum time between alerts in seconds
        """
        self.ear_threshold = ear_threshold
        self.consecutive_frames_threshold = consecutive_frames_threshold
        self.alert_cooldown = alert_cooldown
        
        # Initialize components
        self.ear_calculator = EARCalculator()
        self.alert_service = AlertService()
        self.db_repository = AlertRepository()
        
        # Detection state
        self.consecutive_frames = 0
        self.is_drowsy = False
        self.last_alert_time = 0
        self.detection_start_time = None
        self.session_id = None
        
        # Statistics
        self.total_frames_processed = 0
        self.total_drowsy_frames = 0
        self.total_alerts = 0
        
        # Current state
        self.current_ear = 0.0
        self.current_left_ear = 0.0
        self.current_right_ear = 0.0
        self.detection_active = False
    
    def start_detection_session(self) -> int:
        """
        Start a new detection session.
        
        Returns:
            Session ID
        """
        self.detection_start_time = time.time()
        self.session_id = self.db_repository.start_session()
        self.detection_active = True
        self.reset_statistics()
        return self.session_id
    
    def stop_detection_session(self) -> Dict:
        """
        Stop the current detection session.
        
        Returns:
            Session summary statistics
        """
        if self.session_id:
            self.db_repository.end_session(self.session_id)
        
        self.detection_active = False
        duration = 0.0
        
        if self.detection_start_time:
            duration = time.time() - self.detection_start_time
        
        summary = self.get_session_summary()
        summary['session_duration'] = duration
        
        return summary
    
    def process_frame(self, landmarks) -> Dict:
        """
        Process a frame with facial landmarks and detect drowsiness.
        
        Args:
            landmarks: Facial landmarks array from video processor
            
        Returns:
            Dictionary with detection results and current state
        """
        if not self.detection_active or landmarks is None:
            return self._get_default_result()
        
        self.total_frames_processed += 1
        
        # Calculate EAR for current frame
        left_ear, right_ear, avg_ear = self.ear_calculator.calculate_both_eyes_ear(landmarks)
        
        self.current_left_ear = left_ear
        self.current_right_ear = right_ear
        self.current_ear = avg_ear
        print("EAR:", avg_ear)

        # Check for drowsiness
        drowsy_frame = avg_ear < self.ear_threshold
        
        if drowsy_frame:
            self.consecutive_frames += 1
            self.total_drowsy_frames += 1
            
            # Check if we should trigger an alert
            if (self.consecutive_frames >= self.consecutive_frames_threshold and 
                not self.is_drowsy and 
                self._can_trigger_alert()):
                
                self._trigger_drowsiness_alert(avg_ear, self.consecutive_frames)
                
        else:
            # Reset consecutive frame count if eyes are open
            if self.consecutive_frames > 0:
                # If we were in a drowsy state, stop the alert
                if self.is_drowsy:
                    self._stop_drowsiness_alert()
                
                self.consecutive_frames = 0
        
        return self._get_detection_result()
    
    def _trigger_drowsiness_alert(self, ear_value: float, consecutive_frames: int) -> None:
        """
        Trigger a drowsiness alert.
        
        Args:
            ear_value: EAR value that triggered the alert
            consecutive_frames: Number of consecutive frames below threshold
        """
        self.is_drowsy = True
        self.last_alert_time = time.time()
        self.total_alerts += 1
        
        # Determine alert severity
        severity = self._determine_alert_severity(consecutive_frames)
        
        # Trigger alert service
        self.alert_service.trigger_alert(ear_value, consecutive_frames)
        
        # Log to database
        self.db_repository.log_alert(
            ear_value=ear_value,
            consecutive_frames=consecutive_frames,
            severity=severity,
            notes=f"Session {self.session_id}"
        )
    
    def _stop_drowsiness_alert(self) -> None:
        """Stop the current drowsiness alert."""
        if self.is_drowsy:
            duration = self.alert_service.stop_alert()
            self.is_drowsy = False
            
            # Update database with alert duration if available
            if duration and hasattr(self, '_last_alert_id'):
                # Note: In a more complete implementation, you would update
                # the alert record with the duration
                pass
    
    def _can_trigger_alert(self) -> bool:
        """
        Check if enough time has passed since last alert.
        
        Returns:
            True if alert can be triggered, False otherwise
        """
        current_time = time.time()
        return (current_time - self.last_alert_time) >= self.alert_cooldown
    
    def _determine_alert_severity(self, consecutive_frames: int) -> str:
        """
        Determine alert severity based on consecutive frames.
        
        Args:
            consecutive_frames: Number of consecutive frames below threshold
            
        Returns:
            Severity level ('LOW', 'MEDIUM', 'HIGH')
        """
        if consecutive_frames < 30:
            return 'LOW'
        elif consecutive_frames < 60:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _get_detection_result(self) -> Dict:
        """
        Get current detection result.
        
        Returns:
            Dictionary with current detection state and metrics
        """
        return {
            'ear_value': self.current_ear,
            'left_ear': self.current_left_ear,
            'right_ear': self.current_right_ear,
            'consecutive_frames': self.consecutive_frames,
            'is_drowsy': self.is_drowsy,
            'detection_active': self.detection_active,
            'alert_status': self.alert_service.get_alert_status(),
            'frames_processed': self.total_frames_processed,
            'drowsy_frames': self.total_drowsy_frames,
            'total_alerts': self.total_alerts,
            'ear_threshold': self.ear_threshold,
            'frame_threshold': self.consecutive_frames_threshold
        }
    
    def _get_default_result(self) -> Dict:
        """
        Get default result when detection is not active.
        
        Returns:
            Dictionary with default values
        """
        return {
            'ear_value': 0.0,
            'left_ear': 0.0,
            'right_ear': 0.0,
            'consecutive_frames': 0,
            'is_drowsy': False,
            'detection_active': False,
            'alert_status': {'is_alerting': False, 'duration': 0.0},
            'frames_processed': 0,
            'drowsy_frames': 0,
            'total_alerts': 0,
            'ear_threshold': self.ear_threshold,
            'frame_threshold': self.consecutive_frames_threshold
        }
    
    def get_ear_history(self) -> List[float]:
        """
        Get EAR value history for charting.
        
        Returns:
            List of recent EAR values
        """
        return self.ear_calculator.get_ear_history()
    
    def get_session_summary(self) -> Dict:
        """
        Get summary of current detection session.
        
        Returns:
            Dictionary with session statistics
        """
        drowsiness_rate = 0.0
        if self.total_frames_processed > 0:
            drowsiness_rate = (self.total_drowsy_frames / self.total_frames_processed) * 100
        
        return {
            'session_id': self.session_id,
            'frames_processed': self.total_frames_processed,
            'drowsy_frames': self.total_drowsy_frames,
            'total_alerts': self.total_alerts,
            'drowsiness_rate': drowsiness_rate,
            'current_ear': self.current_ear,
            'consecutive_frames': self.consecutive_frames,
            'is_active': self.detection_active
        }
    
    def update_settings(self, 
                       ear_threshold: Optional[float] = None,
                       consecutive_frames_threshold: Optional[int] = None,
                       alert_cooldown: Optional[float] = None) -> None:
        """
        Update detection settings.
        
        Args:
            ear_threshold: New EAR threshold (optional)
            consecutive_frames_threshold: New consecutive frames threshold (optional)
            alert_cooldown: New alert cooldown period (optional)
        """
        if ear_threshold is not None and 0.1 <= ear_threshold <= 0.5:
            self.ear_threshold = ear_threshold
        
        if consecutive_frames_threshold is not None and consecutive_frames_threshold > 0:
            self.consecutive_frames_threshold = consecutive_frames_threshold
        
        if alert_cooldown is not None and alert_cooldown >= 0:
            self.alert_cooldown = alert_cooldown
    
    def reset_statistics(self) -> None:
        """Reset session statistics."""
        self.total_frames_processed = 0
        self.total_drowsy_frames = 0
        self.total_alerts = 0
        self.consecutive_frames = 0
        self.is_drowsy = False
        self.ear_calculator.reset_history()
    
    def get_alert_service(self) -> AlertService:
        """
        Get the alert service instance.
        
        Returns:
            AlertService instance
        """
        return self.alert_service
    
    def get_database_repository(self) -> AlertRepository:
        """
        Get the database repository instance.
        
        Returns:
            AlertRepository instance
        """
        return self.db_repository
    
    def cleanup(self) -> None:
        """Clean up detector resources."""
        if self.detection_active:
            self.stop_detection_session()
        
        self.alert_service.cleanup()
        
        # Stop any ongoing alerts
        if self.is_drowsy:
            self._stop_drowsiness_alert()