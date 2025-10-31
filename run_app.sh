#!/bin/bash

# Drowsiness Detection App Launcher Script
# This script sets up the environment and runs the Streamlit app

set -e  # Exit on any error

echo "🚀 Drowsiness Detection App Launcher"
echo "===================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python is not installed or not in PATH"
        echo "Please install Python 3.7+ and try again"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "✅ Python found: $($PYTHON_CMD --version)"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found in current directory"
    echo "Please run this script from the drowsiness_app directory"
    exit 1
fi

# Check if virtual environment should be created
if [ "$1" = "--setup" ]; then
    echo "🔧 Setting up virtual environment..."
    
    # Create virtual environment
    $PYTHON_CMD -m venv venv
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo "✅ Virtual environment activated (Linux/Mac)"
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
        echo "✅ Virtual environment activated (Windows)"
    else
        echo "⚠️  Could not activate virtual environment"
    fi
    
    # Install requirements
    echo "📦 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Run setup script
    echo "⚙️  Running setup..."
    $PYTHON_CMD setup.py
    
    echo "🎉 Setup complete!"
fi

# Check if requirements are installed
echo "📦 Checking dependencies..."
$PYTHON_CMD -c "import streamlit, cv2, numpy" 2>/dev/null || {
    echo "❌ Dependencies not installed"
    echo "Run: $0 --setup"
    echo "Or: pip install -r requirements.txt"
    exit 1
}

# Check if dlib predictor exists
if [ ! -f "shape_predictor_68_face_landmarks.dat" ]; then
    echo "⚠️  Face predictor file not found"
    echo "Downloading predictor file..."
    $PYTHON_CMD -c "
import urllib.request, bz2, shutil
url = 'http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2'
print('Downloading...')
urllib.request.urlretrieve(url, 'temp.bz2')
print('Extracting...')
with bz2.BZ2File('temp.bz2', 'rb') as f_in:
    with open('shape_predictor_68_face_landmarks.dat', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
import os; os.remove('temp.bz2')
print('✅ Predictor file ready')
"
fi

# Check if streamlit is available
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found in PATH"
    echo "Install with: pip install streamlit"
    exit 1
fi

echo "🌐 Starting Drowsiness Detection App..."
echo "The app will open at: http://localhost:8501"
echo "Press Ctrl+C to stop the app"
echo ""

# Run the Streamlit app
streamlit run app.py