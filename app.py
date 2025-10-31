"""
Streamlit Drowsiness Detection App

A real-time drowsiness detection application using Eye Aspect Ratio (EAR)
algorithm with OpenCV and dlib for facial landmark detection.
"""

import streamlit as st
import cv2
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import pandas as pd
from modules.video_processor import VideoProcessor
from modules.detector import DrowsinessDetector
from modules.utils import format_timestamp
from PIL import Image
import threading
import atexit

# Page configuration
st.set_page_config(
    page_title="Drowsiness Detection App",
    page_icon="😴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'video_processor' not in st.session_state:
    st.session_state.video_processor = None
if 'detector' not in st.session_state:
    st.session_state.detector = None
if 'detection_running' not in st.session_state:
    st.session_state.detection_running = False
if 'ear_data' not in st.session_state:
    st.session_state.ear_data = []
if 'frame_counter' not in st.session_state:
    st.session_state.frame_counter = 0
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Detection"

# Cleanup function
def cleanup_resources():
    """Clean up resources when app closes."""
    if st.session_state.video_processor:
        st.session_state.video_processor.cleanup()
    if st.session_state.detector:
        st.session_state.detector.cleanup()

# Register cleanup function
atexit.register(cleanup_resources)

def initialize_components():
    """Initialize video processor and detector."""
    if st.session_state.video_processor is None:
        st.session_state.video_processor = VideoProcessor()
    
    if st.session_state.detector is None:
        st.session_state.detector = DrowsinessDetector(
            ear_threshold=0.25,
            consecutive_frames_threshold=20,
            alert_cooldown=5.0
        )

def main():
    """Main application function."""
    
    # Custom CSS for styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    
    .alert-box {
        background: #ff4444;
        color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin: 10px 0;
        animation: blink 1s linear infinite;
    }
    
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .status-running {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-stopped {
        color: #dc3545;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # App header
    st.markdown("""
    <div class="main-header">
        <h1>😴 Drowsiness Detection System</h1>
        <p>Real-time driver drowsiness detection using Eye Aspect Ratio (EAR)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize components
    initialize_components()
    
    # Sidebar for navigation and controls
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox("Select Page", ["Detection", "History", "Settings"])
        st.session_state.current_page = page
        
        st.divider()
        
        # Camera controls
        st.header("Camera Controls")
        
        camera_index = st.selectbox("Camera Source", [0, 1, 2], index=0)
        
        if st.button("Initialize Camera", type="primary"):
            with st.spinner("Initializing camera..."):
                success = st.session_state.video_processor.initialize_camera(camera_index)
                if success:
                    st.success("Camera initialized successfully!")
                else:
                    st.error("Failed to initialize camera. Please check your camera connection.")
        
        # Detection controls
        st.header("Detection Controls")
        
        if not st.session_state.detection_running:
            if st.button("Start Detection", type="primary"):
                start_detection()
        else:
            if st.button("Stop Detection", type="secondary"):
                stop_detection()
        
        # Display current status
        if st.session_state.detection_running:
            st.markdown('<p class="status-running">🟢 Detection Active</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-stopped">🔴 Detection Stopped</p>', unsafe_allow_html=True)
        
        # Camera info
        if st.session_state.video_processor and st.session_state.video_processor.is_camera_active():
            st.divider()
            st.header("Camera Info")
            camera_info = st.session_state.video_processor.get_camera_info()
            st.text(f"Resolution: {camera_info.get('width', 'N/A')}x{camera_info.get('height', 'N/A')}")
            st.text(f"FPS: {camera_info.get('fps', 'N/A'):.1f}")
    
    # Main content based on selected page
    if st.session_state.current_page == "Detection":
        show_detection_page()
    elif st.session_state.current_page == "History":
        show_history_page()
    elif st.session_state.current_page == "Settings":
        show_settings_page()

def start_detection():
    """Start drowsiness detection."""
    if st.session_state.video_processor and st.session_state.video_processor.is_camera_active():
        st.session_state.video_processor.start_capture()
        st.session_state.detector.start_detection_session()
        st.session_state.detection_running = True
        st.session_state.ear_data = []
        st.session_state.frame_counter = 0
        st.success("Detection started!")
    else:
        st.error("Please initialize camera first!")

def stop_detection():
    """Stop drowsiness detection."""
    if st.session_state.video_processor:
        st.session_state.video_processor.stop_capture()
    if st.session_state.detector:
        summary = st.session_state.detector.stop_detection_session()
        st.session_state.detection_running = False
        st.success(f"Detection stopped! Processed {summary.get('frames_processed', 0)} frames.")

def show_detection_page():
    """Show the main detection page."""
    
    # Create columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Live Video Feed")
        video_placeholder = st.empty()
        
        # Alert placeholder
        alert_placeholder = st.empty()
        
    with col2:
        st.header("Detection Metrics")
        metrics_placeholder = st.empty()
        
        st.header("EAR Chart")
        chart_placeholder = st.empty()
    
    # Real-time updates if detection is running
    if st.session_state.detection_running:
        # Get current frame and landmarks
        frame, landmarks = st.session_state.video_processor.get_current_frame_and_landmarks()
        
        if frame is not None:
            # Process frame for drowsiness detection
            detection_result = st.session_state.detector.process_frame(landmarks)
            
            # Update EAR data for charting
            st.session_state.ear_data.append({
                'frame': st.session_state.frame_counter,
                'ear': detection_result['ear_value'],
                'timestamp': datetime.now()
            })
            
            # Keep only last 100 points
            if len(st.session_state.ear_data) > 100:
                st.session_state.ear_data = st.session_state.ear_data[-100:]
            
            st.session_state.frame_counter += 1
            
            # Display video frame
            display_frame = st.session_state.video_processor.get_frame_with_annotations(
                show_landmarks=True, show_face_box=False
            )
            
            if display_frame is not None:
                # Convert BGR to RGB for display
                display_frame_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
                video_placeholder.image(display_frame_rgb, channels="RGB", use_column_width=True)
            
            # Display alert if drowsy
            if detection_result['is_drowsy']:
                alert_service = st.session_state.detector.get_alert_service()
                alert_service.display_visual_alert(alert_placeholder)
            else:
                alert_placeholder.empty()
            
            # Update metrics
            update_metrics_display(metrics_placeholder, detection_result)
            
            # Update EAR chart
            update_ear_chart(chart_placeholder)
            
        # Auto-refresh
        time.sleep(0.1)
        st.rerun()
    
    else:
        video_placeholder.info("Click 'Start Detection' to begin monitoring")
        metrics_placeholder.info("Detection metrics will appear here")
        chart_placeholder.info("EAR chart will appear here")

def update_metrics_display(placeholder, detection_result):
    """Update the metrics display."""
    with placeholder.container():
        # Current EAR
        ear_color = "red" if detection_result['ear_value'] < detection_result['ear_threshold'] else "green"
        st.metric("Current EAR", f"{detection_result['ear_value']:.3f}")
        
        # Consecutive frames
        frame_color = "red" if detection_result['consecutive_frames'] > 10 else "green"
        st.metric("Consecutive Frames", detection_result['consecutive_frames'])
        
        # Status indicators
        if detection_result['is_drowsy']:
            st.error("🚨 DROWSINESS DETECTED")
        else:
            st.success("👁️ ALERT")
        
        # Session statistics
        st.divider()
        st.subheader("Session Stats")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Frames Processed", detection_result['frames_processed'])
            st.metric("Total Alerts", detection_result['total_alerts'])
        
        with col2:
            st.metric("Drowsy Frames", detection_result['drowsy_frames'])
            drowsiness_rate = 0
            if detection_result['frames_processed'] > 0:
                drowsiness_rate = (detection_result['drowsy_frames'] / detection_result['frames_processed']) * 100
            st.metric("Drowsiness Rate", f"{drowsiness_rate:.1f}%")

def update_ear_chart(placeholder):
    """Update the EAR trend chart."""
    if not st.session_state.ear_data:
        return
    
    # Create DataFrame from EAR data
    df = pd.DataFrame(st.session_state.ear_data)
    
    # Create chart
    fig = go.Figure()
    
    # Add EAR line
    fig.add_trace(go.Scatter(
        x=df['frame'],
        y=df['ear'],
        mode='lines',
        name='EAR',
        line=dict(color='blue', width=2)
    ))
    
    # Add threshold line
    threshold = st.session_state.detector.ear_threshold
    fig.add_hline(y=threshold, line_dash="dash", line_color="red", 
                  annotation_text=f"Threshold ({threshold})")
    
    # Update layout
    fig.update_layout(
        title="Eye Aspect Ratio (EAR) Trend",
        xaxis_title="Frame",
        yaxis_title="EAR Value",
        height=300,
        showlegend=True
    )
    
    placeholder.plotly_chart(fig, use_container_width=True)

def show_history_page():
    """Show the alert history page."""
    st.header("Alert History")
    
    if st.session_state.detector:
        db_repo = st.session_state.detector.get_database_repository()
        
        # Get statistics
        stats = db_repo.get_alert_statistics()
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Alerts", stats['total_alerts'])
        with col2:
            st.metric("Today's Alerts", stats['today_alerts'])
        with col3:
            st.metric("Average EAR", f"{stats['average_ear']:.3f}")
        with col4:
            if stats['last_alert']:
                last_alert_time = format_timestamp(stats['last_alert'])
                st.metric("Last Alert", last_alert_time)
        
        st.divider()
        
        # Recent alerts table
        st.subheader("Recent Alerts")
        recent_alerts = db_repo.get_recent_alerts(limit=20)
        
        if recent_alerts:
            # Convert to DataFrame for better display
            df_alerts = pd.DataFrame(recent_alerts)
            df_alerts['timestamp'] = pd.to_datetime(df_alerts['timestamp'])
            df_alerts = df_alerts.sort_values('timestamp', ascending=False)
            
            # Format for display
            display_df = df_alerts[['timestamp', 'ear_value', 'consecutive_frames', 'severity']].copy()
            display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            display_df.columns = ['Time', 'EAR Value', 'Consecutive Frames', 'Severity']
            
            st.dataframe(display_df, use_container_width=True)
            
            # Severity distribution chart
            if stats['severity_distribution']:
                st.subheader("Alert Severity Distribution")
                severity_df = pd.DataFrame(list(stats['severity_distribution'].items()), 
                                         columns=['Severity', 'Count'])
                
                fig_pie = px.pie(severity_df, values='Count', names='Severity', 
                               title="Alert Distribution by Severity")
                st.plotly_chart(fig_pie, use_container_width=True)
        
        else:
            st.info("No alerts recorded yet.")
        
        # Export functionality
        st.divider()
        st.subheader("Export Data")
        if st.button("Export Alerts to CSV"):
            export_path = f"alerts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            if db_repo.export_alerts_to_csv(export_path):
                st.success(f"Alerts exported to {export_path}")
            else:
                st.error("Failed to export alerts")

def show_settings_page():
    """Show the settings configuration page."""
    st.header("Detection Settings")
    
    if st.session_state.detector:
        # Current settings
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Detection Parameters")
            
            # EAR threshold
            ear_threshold = st.slider(
                "EAR Threshold",
                min_value=0.15,
                max_value=0.35,
                value=st.session_state.detector.ear_threshold,
                step=0.01,
                help="Lower values make detection more sensitive"
            )
            
            # Consecutive frames threshold
            frame_threshold = st.slider(
                "Consecutive Frames Threshold",
                min_value=10,
                max_value=50,
                value=st.session_state.detector.consecutive_frames_threshold,
                step=1,
                help="Number of consecutive frames needed to trigger alert"
            )
            
            # Alert cooldown
            alert_cooldown = st.slider(
                "Alert Cooldown (seconds)",
                min_value=1.0,
                max_value=10.0,
                value=st.session_state.detector.alert_cooldown,
                step=0.5,
                help="Minimum time between alerts"
            )
        
        with col2:
            st.subheader("Alert Settings")
            
            alert_service = st.session_state.detector.get_alert_service()
            
            # Sound alerts
            sound_enabled = st.checkbox(
                "Enable Sound Alerts",
                value=alert_service.sound_enabled
            )
            
            # Visual alerts
            visual_enabled = st.checkbox(
                "Enable Visual Alerts",
                value=alert_service.visual_alert_enabled
            )
            
            # Detection confidence
            detection_confidence = st.slider(
                "Face Detection Confidence",
                min_value=0.3,
                max_value=0.9,
                value=0.5,
                step=0.1,
                help="Higher values require more confident face detection"
            )
        
        # Apply settings
        if st.button("Apply Settings", type="primary"):
            # Update detector settings
            st.session_state.detector.update_settings(
                ear_threshold=ear_threshold,
                consecutive_frames_threshold=frame_threshold,
                alert_cooldown=alert_cooldown
            )
            
            # Update alert service settings
            alert_service.enable_sound_alerts(sound_enabled)
            alert_service.enable_visual_alerts(visual_enabled)
            
            # Update video processor settings
            if st.session_state.video_processor:
                st.session_state.video_processor.set_detection_confidence(detection_confidence)
            
            st.success("Settings updated successfully!")
        
        # Reset to defaults
        if st.button("Reset to Defaults"):
            st.session_state.detector.update_settings(
                ear_threshold=0.25,
                consecutive_frames_threshold=20,
                alert_cooldown=5.0
            )
            st.success("Settings reset to defaults!")
        
        st.divider()
        
        # System information
        st.subheader("System Information")
        
        st.info("""
        **Installation Instructions:**
        1. Install required packages: `pip install -r requirements.txt`
        2. Download dlib's face predictor: [shape_predictor_68_face_landmarks.dat](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)
        3. Extract the .dat file to the project directory
        4. Run the app: `streamlit run app.py`
        
        **About EAR Algorithm:**
        - EAR (Eye Aspect Ratio) measures eye openness
        - Normal EAR: ~0.3, Closed eyes: ~0.1-0.2
        - Lower threshold = more sensitive detection
        - Higher consecutive frames = fewer false positives
        """)

if __name__ == "__main__":
    main()