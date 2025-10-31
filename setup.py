#!/usr/bin/env python3
"""
Setup script for the Drowsiness Detection App.

This script helps set up the environment and download required files.
"""

import os
import sys
import subprocess
import urllib.request
import bz2
import shutil
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version {sys.version} is compatible.")
    return True


def install_requirements():
    """Install Python requirements."""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies.")
        return False


def download_dlib_predictor():
    """Download dlib's facial landmark predictor."""
    predictor_path = "shape_predictor_68_face_landmarks.dat"
    
    if os.path.exists(predictor_path):
        print(f"✅ {predictor_path} already exists.")
        return True
    
    print("\n⬇️  Downloading dlib facial landmark predictor...")
    print("This may take a few minutes (68MB download)...")
    
    url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
    compressed_path = "shape_predictor_68_face_landmarks.dat.bz2"
    
    try:
        # Download compressed file
        urllib.request.urlretrieve(url, compressed_path)
        print("✅ Download completed.")
        
        # Extract the file
        print("📂 Extracting predictor file...")
        with bz2.BZ2File(compressed_path, 'rb') as f_in:
            with open(predictor_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove compressed file
        os.remove(compressed_path)
        print(f"✅ {predictor_path} extracted successfully.")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download predictor: {e}")
        print("\n📝 Manual download instructions:")
        print("1. Visit: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
        print("2. Extract the .dat file to this directory")
        return False


def check_camera():
    """Check if camera is available."""
    print("\n📹 Checking camera availability...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                print("✅ Camera is working properly.")
                return True
        print("⚠️  Camera not detected or not working.")
        print("Make sure your camera is connected and not being used by other applications.")
        return False
    except ImportError:
        print("⚠️  OpenCV not available to test camera.")
        return False


def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")
    directories = ["logs", "exports"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")


def run_tests():
    """Run basic import tests."""
    print("\n🧪 Running import tests...")
    
    required_modules = [
        "streamlit",
        "cv2",
        "dlib", 
        "numpy",
        "scipy",
        "plotly",
        "pandas",
        "PIL"
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n⚠️  Failed to import: {', '.join(failed_imports)}")
        print("Try running: pip install -r requirements.txt")
        return False
    
    print("✅ All modules imported successfully.")
    return True


def main():
    """Main setup function."""
    print("🚀 Drowsiness Detection App Setup")
    print("=" * 40)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install requirements
    if success and not install_requirements():
        success = False
    
    # Download dlib predictor
    if success:
        download_dlib_predictor()  # Don't fail if this doesn't work
    
    # Create directories
    if success:
        create_directories()
    
    # Run tests
    if success and not run_tests():
        success = False
    
    # Check camera
    check_camera()  # Don't fail if camera not available
    
    print("\n" + "=" * 40)
    
    if success:
        print("🎉 Setup completed successfully!")
        print("\n🚀 To start the application:")
        print("   streamlit run app.py")
        print("\n🌐 The app will open at: http://localhost:8501")
    else:
        print("❌ Setup encountered some issues.")
        print("Please check the error messages above.")
    
    print("\n📖 For more information, see README.md")


if __name__ == "__main__":
    main()