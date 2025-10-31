"""
Alert service for drowsiness detection notifications.

This module handles audio alerts, visual notifications, and alert management
for the drowsiness detection system.
"""

import time
import threading
from typing import Optional, Callable
import streamlit as st


class AlertService:
    """Service class for managing drowsiness alerts and notifications."""
    
    def __init__(self):
        """Initialize the AlertService."""
        self.is_alerting = False
        self.alert_start_time = None
        self.alert_thread = None
        self.alert_callback = None
        self.sound_enabled = True
        self.visual_alert_enabled = True
        
    def set_alert_callback(self, callback: Callable) -> None:
        """
        Set callback function to be called when alert is triggered.
        
        Args:
            callback: Function to call when alert is triggered
        """
        self.alert_callback = callback
    
    def enable_sound_alerts(self, enabled: bool = True) -> None:
        """
        Enable or disable sound alerts.
        
        Args:
            enabled: True to enable sound alerts, False to disable
        """
        self.sound_enabled = enabled
    
    def enable_visual_alerts(self, enabled: bool = True) -> None:
        """
        Enable or disable visual alerts.
        
        Args:
            enabled: True to enable visual alerts, False to disable
        """
        self.visual_alert_enabled = enabled
    
    def trigger_alert(self, ear_value: float, consecutive_frames: int) -> None:
        """
        Trigger drowsiness alert.
        
        Args:
            ear_value: Current EAR value that triggered the alert
            consecutive_frames: Number of consecutive frames below threshold
        """
        if not self.is_alerting:
            self.is_alerting = True
            self.alert_start_time = time.time()
            
            # Start alert in separate thread to avoid blocking
            self.alert_thread = threading.Thread(
                target=self._run_alert,
                args=(ear_value, consecutive_frames),
                daemon=True
            )
            self.alert_thread.start()
    
    def stop_alert(self) -> Optional[float]:
        """
        Stop current alert and return duration.
        
        Returns:
            Alert duration in seconds, or None if no active alert
        """
        if self.is_alerting and self.alert_start_time:
            duration = time.time() - self.alert_start_time
            self.is_alerting = False
            self.alert_start_time = None
            return duration
        return None
    
    def _run_alert(self, ear_value: float, consecutive_frames: int) -> None:
        """
        Run the alert sequence (internal method).
        
        Args:
            ear_value: EAR value that triggered the alert
            consecutive_frames: Number of consecutive frames below threshold
        """
        # Play sound alert if enabled
        if self.sound_enabled:
            # Play sound in a separate thread so UI/main processing never blocks
            try:
                threading.Thread(target=self._play_alert_sound, daemon=True).start()
            except Exception:
                # If threading fails for any reason, fallback to direct call
                self._play_alert_sound()
        
        # Call callback if set
        if self.alert_callback:
            self.alert_callback(ear_value, consecutive_frames)
    
    def _play_alert_sound(self) -> None:
        """Play alert sound (internal method)."""
        try:
            # First, prefer a bundled alert.wav if present at repo root or module folder
            import os
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            possible_locations = [
                os.path.join(repo_root, 'alert.wav'),
                os.path.join(os.path.dirname(__file__), 'alert.wav')
            ]

            alert_file = None
            for p in possible_locations:
                if os.path.isfile(p):
                    alert_file = p
                    break

            if alert_file:
                # Play the file using playsound (in this thread _play_alert_sound is already threaded)
                try:
                    from playsound import playsound
                    playsound(alert_file)
                    return
                except Exception:
                    # If playsound fails, continue to generated beep fallback
                    pass

            # If no alert.wav found or playing it failed, generate a beep sound
            self._play_beep_sound()
        except Exception:
            # Fallback to system beep
            self._play_system_beep()
    
    def _play_beep_sound(self) -> None:
        """Play beep sound using playsound library."""
        try:
            # Create a simple beep sound programmatically
            import numpy as np
            from scipy.io.wavfile import write
            import tempfile
            import os
            
            # Generate a simple beep tone
            sample_rate = 44100
            duration = 0.5  # seconds
            frequency = 800  # Hz
            
            # Generate sine wave
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            wave = np.sin(frequency * 2 * np.pi * t)
            
            # Apply fade in/out to avoid clicks
            fade_frames = int(0.01 * sample_rate)  # 10ms fade
            wave[:fade_frames] *= np.linspace(0, 1, fade_frames)
            wave[-fade_frames:] *= np.linspace(1, 0, fade_frames)
            
            # Convert to 16-bit integers
            wave = (wave * 32767).astype(np.int16)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                temp_path = tmp_file.name
                write(temp_path, sample_rate, wave)
            
            # Play the sound
            try:
                from playsound import playsound
                playsound(temp_path)
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        except ImportError:
            # If scipy/numpy not available, fall back to system beep
            self._play_system_beep()
        except Exception:
            # Any other error, fall back to system beep
            self._play_system_beep()
    
    def _play_system_beep(self) -> None:
        """Play system beep as fallback."""
        try:
            import os
            import platform
            
            system = platform.system().lower()
            
            if system == 'darwin':  # macOS
                os.system('afplay /System/Library/Sounds/Ping.aiff')
            elif system == 'linux':
                os.system('beep -f 800 -l 500')  # If beep package is installed
            elif system == 'windows':
                import winsound
                winsound.Beep(800, 500)  # 800 Hz for 500ms
            else:
                # Generic fallback
                print('\a')  # ASCII bell character
                
        except Exception:
            # Final fallback
            print('\a')  # ASCII bell character
    
    def get_visual_alert_style(self) -> dict:
        """
        Get CSS style for visual alert display.
        
        Returns:
            Dictionary with CSS properties for alert styling
        """
        if not self.is_alerting or not self.visual_alert_enabled:
            return {}
        
        return {
            'background-color': '#ff4444',
            'color': 'white',
            'padding': '20px',
            'border-radius': '10px',
            'border': '3px solid #cc0000',
            'text-align': 'center',
            'font-weight': 'bold',
            'font-size': '18px',
            'animation': 'blink 1s linear infinite'
        }
    
    def display_visual_alert(self, container) -> None:
        """
        Display visual alert in Streamlit container.
        
        Args:
            container: Streamlit container to display alert in
        """
        if self.is_alerting and self.visual_alert_enabled:
            with container:
                st.error("🚨 DROWSINESS DETECTED! 🚨")
                st.markdown("""
                    <div style='
                        background-color: #ff4444;
                        color: white;
                        padding: 15px;
                        border-radius: 8px;
                        text-align: center;
                        font-weight: bold;
                        font-size: 16px;
                        margin: 10px 0;
                        border: 2px solid #cc0000;
                    '>
                        ⚠️ WAKE UP! DRIVER DROWSINESS DETECTED! ⚠️
                    </div>
                """, unsafe_allow_html=True)
    
    def get_alert_status(self) -> dict:
        """
        Get current alert status information.
        
        Returns:
            Dictionary with alert status information
        """
        duration = 0.0
        if self.is_alerting and self.alert_start_time:
            duration = time.time() - self.alert_start_time
        
        return {
            'is_alerting': self.is_alerting,
            'duration': duration,
            'sound_enabled': self.sound_enabled,
            'visual_enabled': self.visual_alert_enabled
        }
    
    def get_alert_message(self, ear_value: float, consecutive_frames: int) -> str:
        """
        Get formatted alert message.
        
        Args:
            ear_value: Current EAR value
            consecutive_frames: Number of consecutive frames below threshold
            
        Returns:
            Formatted alert message string
        """
        severity = self._determine_severity(consecutive_frames)
        
        messages = {
            'LOW': f"💤 Mild drowsiness detected (EAR: {ear_value:.3f})",
            'MEDIUM': f"😴 Moderate drowsiness detected (EAR: {ear_value:.3f})",
            'HIGH': f"🚨 SEVERE drowsiness detected! (EAR: {ear_value:.3f})"
        }
        
        return messages.get(severity, f"Drowsiness detected (EAR: {ear_value:.3f})")
    
    def _determine_severity(self, consecutive_frames: int) -> str:
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
    
    def cleanup(self) -> None:
        """Clean up alert service resources."""
        self.stop_alert()
        if self.alert_thread and self.alert_thread.is_alive():
            self.alert_thread.join(timeout=1.0)