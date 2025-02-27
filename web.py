from flask import Flask, render_template, Response, request, jsonify, url_for
import cv2
import face_recognition
import pandas as pd
import datetime
import pickle
import os

app = Flask(__name__)

# Load known face encodings and names from encodings.pkl
known_face_encodings = []
known_face_names = []

# Load the face encodings from the encodings.pkl file
encodings_path = "encodings.pkl"
if os.path.exists(encodings_path):
    with open(encodings_path, "rb") as f:
        # Load the encodings and the corresponding names
        data = pickle.load(f)
        known_face_encodings = data["encodings"]
        known_face_names = data["names"]

# Load attendance file
attendance_file = "attendance.xlsx"

def mark_attendance(name):
    """Marks attendance in an Excel sheet if not already marked in the last hour."""
    try:
        df = pd.read_excel(attendance_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Name", "Time"])

    now = datetime.datetime.now()
    one_hour_ago = now - datetime.timedelta(hours=1)

    # Check if the name is already marked in the last hour
    if not ((df["Name"] == name) & (pd.to_datetime(df["Time"], format="%Y-%m-%d %H:%M:%S") > one_hour_ago)).any():
        new_entry = pd.DataFrame({"Name": [name], "Time": [now.strftime("%Y-%m-%d %H:%M:%S")]})
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_excel(attendance_file, index=False)
        print(f"Attendance marked for {name}")
    else:
        print(f"{name} already marked in the last hour")

def generate_frames():
    """Captures webcam video and performs face recognition."""
    camera = cv2.VideoCapture(0)

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                    mark_attendance(name)

                # Draw rectangle and label
                top, right, bottom, left = [v * 4 for v in face_location]
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/attendance')
def attendance_page():
    return render_template('attendance.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/take-attendance', methods=['POST'])
def take_attendance():
    """Starts face recognition and marks attendance when 'Take Attendance' button is clicked."""
    print("Taking attendance...")
    return jsonify({"message": "Attendance process started!"})

if __name__ == '__main__':
    app.run(debug=True)
