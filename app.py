from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
import cv2
import face_recognition
import numpy as np
import os
import subprocess
import sys
import pandas as pd
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from models import db, User, Attendance  

app = Flask(__name__)

# 🔹 Flask Configurations
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 🔹 Initialize Database
db.init_app(app)

# Ensure tables are created
with app.app_context():
    db.create_all()

# 🔹 Load known faces from the 'images' folder
known_faces_dir = 'images'
known_faces = []
known_names = []

for filename in os.listdir(known_faces_dir):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        image_path = os.path.join(known_faces_dir, filename)
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_faces.append(encodings[0])
                known_names.append(os.path.splitext(filename)[0])  # Filename without extension
            else:
                print(f"Warning: No face detected in {filename}. Skipping.")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

# 🔹 Routes
@app.route('/')
def login():
    return render_template('login.html')


@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')  # Ensure you have 'index.html' in the templates folder


@app.route('/login', methods=['POST'])
def authenticate():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        session['user'] = username
        return redirect(url_for('index'))
    else:
        flash("Invalid credentials, please try again.", "danger")
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            print("📌 Received Registration Request")
            print("Form Data:", request.form)  # Debugging form data

            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()

            print(f"Extracted username: {username}, password: {password}, confirm_password: {confirm_password}")

            # ✅ Ensure username is provided
            if not username:
                flash("❌ Username is required!", "danger")
                print("❌ Error: Username is empty")
                return redirect(url_for('register'))

            # ✅ Ensure passwords are provided and match
            if not password or not confirm_password:
                flash("❌ Password fields cannot be empty!", "danger")
                print("❌ Error: Passwords are empty")
                return redirect(url_for('register'))

            if password != confirm_password:
                flash("❌ Passwords do not match!", "danger")
                print("❌ Error: Passwords do not match")
                return redirect(url_for('register'))

            # ✅ Hash the password
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

            # ✅ Check if username already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash("❌ Username already exists! Choose a different one.", "danger")
                print("❌ Error: Username already taken")
                return redirect(url_for('register'))

            # ✅ Add user to database
            new_user = User(username=username, password_hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            flash("✅ Registration successful! Now capturing face...", "success")
            print("✅ User registered successfully:", username)

            # ✅ Run capture_face.py using subprocess
            result = subprocess.run(["python", "capture_face.py", username], capture_output=True, text=True)

            print("📷 Face Capture Output:", result.stdout)
            print("⚠️ Face Capture Errors:", result.stderr)

            if result.returncode == 0:
                flash("✅ Face captured successfully!", "success")
            else:
                flash("⚠️ Face capture failed. Please try again.", "warning")

            return redirect(url_for('login'))

        except Exception as e:
            print("❌ Registration Error:", str(e))  # ✅ Print exact error message
            flash(f"❌ Error occurred while registering student: {str(e)}", "danger")
            db.session.rollback()
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/attendance')
def attendance():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('attendance.html')


@app.route('/attendance_data')
def attendance_data():
    # Fetch attendance data from the database or file
    attendance = db.session.query(Attendance).all()  # Or read from Excel file
    data = []
    for record in attendance:
        data.append({
            'id': record.id,
            'name': record.name,
            'date': record.date,
            'time': record.time
        })
    return jsonify(data)


#  **Face Recognition & Attendance Marking**
@app.route('/capture', methods=['POST'])
def capture():
    if 'user' not in session:
        return jsonify({"message": "Unauthorized"}), 401

    try:
        video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not video_capture.isOpened():
            return jsonify({"message": "Error: Could not access the webcam"}), 400

        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            if not face_encodings:
                continue  

            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(known_faces, face_encoding)
                face_distances = face_recognition.face_distance(known_faces, face_encoding)

                if any(matches):
                    best_match_index = np.argmin(face_distances)
                    name = known_names[best_match_index]

                    now = datetime.now()
                    date_str = now.strftime("%Y-%m-%d")
                    time_str = now.strftime("%H:%M:%S")

                    # Check if attendance is already marked within the last 1 hour
                    one_hour_ago = now - timedelta(hours=1)
                    last_attendance = Attendance.query.filter_by(name=name, date=date_str).order_by(Attendance.time.desc()).first()

                    if last_attendance:
                        last_time = datetime.strptime(f"{last_attendance.date} {last_attendance.time}", "%Y-%m-%d %H:%M:%S")
                        if now - timedelta(hours=1) <= last_time <= now:
                            return jsonify({"message": f"{name} recognized, but attendance already marked within the last hour."})

                    # Mark attendance in database
                    new_entry = Attendance(name=name, date=date_str, time=time_str)
                    db.session.add(new_entry)
                    db.session.commit()

                    # Save Attendance in Excel File
                    excel_path = "attendance_records.xlsx"
                    if not os.path.exists(excel_path):
                        df = pd.DataFrame(columns=["Name", "Date", "Time"])
                        df.to_excel(excel_path, index=False)

                    df = pd.read_excel(excel_path)
                    new_entry_df = pd.DataFrame([[name, date_str, time_str]], columns=["Name", "Date", "Time"])
                    df = pd.concat([df, new_entry_df], ignore_index=True)
                    df.to_excel(excel_path, index=False)

                    print(f"✅ Attendance saved in {excel_path}")

                    return jsonify({"message": f"{name} recognized and attendance marked."})

        return jsonify({"message": "Face not recognized."}), 400

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

    finally:
        video_capture.release()

# **Live Webcam Streaming with Green Face Detection Box**
import time
def generate_frames():
    video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    last_frame_time = time.time()

    while True:
        success, frame = video_capture.read()
        if not success:
            break
        else:
            # Limit the FPS to avoid overloading the server
            current_time = time.time()
            if current_time - last_frame_time >= 1/15:  # 15 FPS
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame)

                for top, right, bottom, left in face_locations:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                _, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                last_frame_time = current_time

    video_capture.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
