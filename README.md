# Drowsiness Detection App

A real-time driver drowsiness detection system built with Streamlit, OpenCV, and dlib using the Eye Aspect Ratio (EAR) algorithm.

## Features

- **Real-time Detection**: Live webcam feed with facial landmark detection
- **EAR Algorithm**: Eye Aspect Ratio calculation for drowsiness detection
- **Smart Alerts**: Audio and visual alerts when drowsiness is detected
- **Database Logging**: SQLite database for storing alert history
- **Interactive Dashboard**: Real-time EAR charts and detection metrics
- **History Tracking**: View past alerts and statistics
- **Configurable Settings**: Adjustable thresholds and alert parameters

## Project Structure

```
drowsiness_app/
│
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── setup.py                    # Setup script
│
└── modules/
    ├── __init__.py             # Package initializer
    ├── video_processor.py      # Video capture and landmark detection
    ├── ear_calculator.py       # Eye Aspect Ratio calculation
    ├── detector.py             # Drowsiness detection logic
    ├── alert_service.py        # Alert notifications
    ├── db_repository.py        # Database operations
    └── utils.py                # Utility functions
```

## Installation

### Prerequisites

1. **Python 3.7+** installed on your system
2. **Webcam** connected and working
3. **Internet connection** for downloading dlib model

### Step 1: Clone and Setup

```bash
# Navigate to your project directory
cd drowsiness-app

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Download dlib Face Predictor

The application requires dlib's 68-point facial landmark predictor:

```bash
# Download the predictor file (68MB)
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2

# Extract the file
bunzip2 shape_predictor_68_face_landmarks.dat.bz2
```

**Alternative Manual Download:**
1. Visit: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
2. Extract the `.dat` file to the `drowsiness_app` directory

### Step 3: Run the Application
.venv\Scripts\activate

```bash
streamlit run app.py
```

The app will open in your default web browser at `http://localhost:8501`

## Usage

### 1. Initialize Camera

1. Open the app in your browser
2. Select your camera from the sidebar dropdown
3. Click "Initialize Camera"
4. Grant camera permissions if prompted

### 2. Start Detection

1. Click "Start Detection" in the sidebar
2. Position yourself in front of the camera
3. The system will begin monitoring your eye movements
4. EAR values and detection metrics will appear in real-time

### 3. Configure Settings

1. Go to the "Settings" page
2. Adjust detection parameters:
   - **EAR Threshold**: Lower = more sensitive (default: 0.25)
   - **Consecutive Frames**: Frames needed to trigger alert (default: 20)
   - **Alert Cooldown**: Time between alerts (default: 5 seconds)
3. Enable/disable sound and visual alerts

### 4. View History

1. Go to the "History" page
2. View alert statistics and recent alerts
3. Export alert data to CSV for analysis

## How It Works

### Eye Aspect Ratio (EAR) Algorithm

The EAR algorithm calculates the ratio of eye height to width using facial landmarks:

```
EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
```

Where p1-p6 are the 6 facial landmarks around each eye.

### Detection Logic

1. **Face Detection**: dlib detects faces in video frames
2. **Landmark Extraction**: 68 facial landmarks are identified
3. **EAR Calculation**: Eye aspect ratios are computed for both eyes
4. **Drowsiness Detection**: EAR below threshold for consecutive frames triggers alert
5. **Alert System**: Audio/visual notifications and database logging

### Typical EAR Values

- **Alert/Normal**: ~0.3
- **Partially Closed**: ~0.2-0.25
- **Closed Eyes**: ~0.1-0.15

## Configuration

### Detection Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| EAR Threshold | 0.25 | 0.15-0.35 | Drowsiness detection threshold |
| Consecutive Frames | 20 | 10-50 | Frames needed to trigger alert |
| Alert Cooldown | 5.0s | 1-10s | Minimum time between alerts |

### Alert Settings

- **Sound Alerts**: Enable/disable audio notifications
- **Visual Alerts**: Enable/disable UI warning messages
- **Detection Confidence**: Face detection sensitivity

## Troubleshooting

### Common Issues

1. **Camera Not Working**
   - Check camera permissions
   - Try different camera indices (0, 1, 2)
   - Ensure no other apps are using the camera

2. **dlib Installation Failed**
   ```bash
   # On Windows, you may need Visual Studio Build Tools
   pip install cmake
   pip install dlib
   
   # Alternative: Use conda
   conda install -c conda-forge dlib
   ```

3. **No Face Detected**
   - Ensure good lighting
   - Position face clearly in camera view
   - Adjust detection confidence in settings

4. **High CPU Usage**
   - Reduce camera resolution
   - Increase frame processing delay
   - Close other applications

### Performance Optimization

- Use lower camera resolution (640x480)
- Reduce frame rate if needed
- Run on systems with good CPU performance
- Ensure sufficient lighting for face detection

## Technical Details

### Dependencies

- **Streamlit**: Web interface and dashboard
- **OpenCV**: Video capture and image processing
- **dlib**: Face detection and landmark prediction
- **NumPy**: Numerical computations
- **SciPy**: Audio generation for alerts
- **Plotly**: Interactive charts and graphs
- **Pandas**: Data manipulation and analysis
- **SQLite3**: Database for alert logging

### Database Schema

**Alerts Table:**
- `id`: Primary key
- `timestamp`: Alert time
- `ear_value`: EAR that triggered alert
- `consecutive_frames`: Frame count
- `duration_seconds`: Alert duration
- `severity`: Alert level (LOW/MEDIUM/HIGH)
- `notes`: Additional information

**Sessions Table:**
- `id`: Session ID
- `start_time`: Session start
- `end_time`: Session end
- `total_alerts`: Alert count
- `session_duration`: Total duration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Acknowledgments

- dlib library for facial landmark detection
- Streamlit for the web interface framework
- OpenCV community for computer vision tools

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review GitHub issues
3. Create a new issue with detailed information

---

**Note**: This application is for educational and research purposes. For production use in safety-critical applications, additional testing and validation are required.