#
pip install -r requirements.txt

# Download the predictor file (68MB)
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2

# Extract the file
bunzip2 shape_predictor_68_face_landmarks.dat.bz2

**Alternative Manual Download:**
1. Visit: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
2. Extract the `.dat` file to the `drowsiness_app` directory

### Run the Application
.venv\Scripts\activate

streamlit run app.py
