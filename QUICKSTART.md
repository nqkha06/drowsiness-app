# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Download Face Predictor
Download the dlib face predictor file (required):
- **Automatic**: Run `python setup.py` 
- **Manual**: Download from [here](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2) and extract to project folder

### Step 3: Run the App
```bash
streamlit run app.py
```

The app will open at: http://localhost:8501

## 📋 Requirements
- Python 3.7+
- Webcam
- ~500MB free space (for dependencies)

## ⚡ Quick Test
```bash
python test_components.py
```

## 🔧 Troubleshooting

**Camera not working?**
- Check camera permissions
- Try different camera index (0, 1, 2)

**dlib installation fails?**
```bash
pip install cmake
pip install dlib
```

**Import errors?**
```bash
pip install --upgrade -r requirements.txt
```

## 📖 Full Documentation
See [README.md](README.md) for complete instructions.