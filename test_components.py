#!/usr/bin/env python3
"""
Demo script for testing individual components of the drowsiness detection system.
Run this to verify that all modules are working correctly.
"""

import sys
import os

# Add the modules directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_utils():
    """Test utility functions."""
    print("Testing utils module...")
    try:
        from modules.utils import euclidean_distance, get_eye_landmarks, validate_ear_threshold
        
        # Test euclidean distance
        distance = euclidean_distance((0, 0), (3, 4))
        assert distance == 5.0, f"Expected 5.0, got {distance}"
        
        # Test EAR threshold validation
        assert validate_ear_threshold(0.25) == True
        assert validate_ear_threshold(0.05) == False
        assert validate_ear_threshold(0.6) == False
        
        print("✅ Utils module tests passed")
        return True
    except Exception as e:
        print(f"❌ Utils module test failed: {e}")
        return False

def test_ear_calculator():
    """Test EAR calculator."""
    print("Testing EAR calculator...")
    try:
        from modules.ear_calculator import EARCalculator
        
        calculator = EARCalculator()
        
        # Test with dummy eye landmarks (6 points)
        eye_landmarks = [(10, 15), (12, 10), (15, 10), (20, 15), (15, 20), (12, 20)]
        ear = calculator.calculate_eye_ear(eye_landmarks)
        
        assert 0.0 <= ear <= 1.0, f"EAR should be between 0 and 1, got {ear}"
        
        print("✅ EAR calculator tests passed")
        return True
    except Exception as e:
        print(f"❌ EAR calculator test failed: {e}")
        return False

def test_database():
    """Test database operations."""
    print("Testing database repository...")
    try:
        from modules.db_repository import AlertRepository
        
        # Create a temporary database
        db_repo = AlertRepository("test_alerts.db")
        
        # Test logging an alert
        alert_id = db_repo.log_alert(
            ear_value=0.20,
            consecutive_frames=25,
            severity='MEDIUM',
            notes='Test alert'
        )
        
        assert alert_id > 0, "Alert ID should be positive"
        
        # Test getting statistics
        stats = db_repo.get_alert_statistics()
        assert stats['total_alerts'] >= 1, "Should have at least one alert"
        
        # Clean up
        os.remove("test_alerts.db")
        
        print("✅ Database repository tests passed")
        return True
    except Exception as e:
        print(f"❌ Database repository test failed: {e}")
        return False

def test_alert_service():
    """Test alert service."""
    print("Testing alert service...")
    try:
        from modules.alert_service import AlertService
        
        alert_service = AlertService()
        
        # Test settings
        alert_service.enable_sound_alerts(False)
        assert alert_service.sound_enabled == False
        
        alert_service.enable_visual_alerts(True)
        assert alert_service.visual_alert_enabled == True
        
        # Test alert message generation
        message = alert_service.get_alert_message(0.20, 25)
        assert "drowsiness detected" in message.lower()
        
        print("✅ Alert service tests passed")
        return True
    except Exception as e:
        print(f"❌ Alert service test failed: {e}")
        return False

def test_detector():
    """Test drowsiness detector."""
    print("Testing drowsiness detector...")
    try:
        from modules.detector import DrowsinessDetector
        
        detector = DrowsinessDetector()
        
        # Test settings update
        detector.update_settings(ear_threshold=0.22, consecutive_frames_threshold=15)
        assert detector.ear_threshold == 0.22
        assert detector.consecutive_frames_threshold == 15
        
        # Test session management
        session_id = detector.start_detection_session()
        assert session_id > 0
        
        summary = detector.stop_detection_session()
        assert 'session_duration' in summary
        
        print("✅ Drowsiness detector tests passed")
        return True
    except Exception as e:
        print(f"❌ Drowsiness detector test failed: {e}")
        return False

def test_imports():
    """Test critical imports."""
    print("Testing critical imports...")
    
    try:
        import numpy as np
        print("✅ NumPy imported")
    except ImportError:
        print("❌ NumPy import failed")
        return False
    
    try:
        import cv2
        print("✅ OpenCV imported")
    except ImportError:
        print("❌ OpenCV import failed - install with: pip install opencv-python")
        return False
    
    try:
        import dlib
        print("✅ dlib imported")
    except ImportError:
        print("❌ dlib import failed - install with: pip install dlib")
        return False
    
    try:
        import streamlit
        print("✅ Streamlit imported")
    except ImportError:
        print("❌ Streamlit import failed - install with: pip install streamlit")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🧪 Drowsiness Detection App - Component Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_utils,
        test_ear_calculator,
        test_database,
        test_alert_service,
        test_detector
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The app should work correctly.")
        print("\n🚀 Next steps:")
        print("1. Make sure you have the dlib predictor file:")
        print("   shape_predictor_68_face_landmarks.dat")
        print("2. Run the app: streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        print("Install missing dependencies with: pip install -r requirements.txt")

if __name__ == "__main__":
    main()