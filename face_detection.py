import cv2
import face_recognition
import pickle
import numpy as np
from attendance import mark_attendance
from custom_logging import log_info, log_error

# Load known face encodings
try:
    with open("encodings.pkl", "rb") as f:
        data = pickle.load(f)
    known_encodings = data.get("encodings", [])
    known_names = data.get("names", [])

    if not known_encodings:
        log_error("No face encodings found in 'encodings.pkl'. Exiting.")
        exit()

    log_info(f"Successfully loaded {len(known_names)} face encodings.")
    print(f"Loaded known faces: {len(known_names)}")

except FileNotFoundError:
    log_error("Error: 'encodings.pkl' not found. Run encode_faces.py first.")
    exit()
except Exception as e:
    log_error(f"Error loading encodings.pkl: {str(e)}")
    exit()

# Track names already marked for attendance
marked_names = set()

def recognize_faces():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        log_error("Error: Could not open webcam.")
        return

    log_info("Started video capture.")

    while True:
        try:
            success, img = cap.read()
            if not success:
                log_error("Failed to capture frame from webcam.")
                break

            # Resize frame for faster processing
            img_small = cv2.resize(img, (0, 0), None, 0.5, 0.5)
            img_small_rgb = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)

            # Detect faces
            faces_cur_frame = face_recognition.face_locations(img_small_rgb)
            encodes_cur_frame = face_recognition.face_encodings(img_small_rgb, faces_cur_frame)

            for encode_face, face_loc in zip(encodes_cur_frame, faces_cur_frame):
                face_dis = face_recognition.face_distance(known_encodings, encode_face)

                if len(face_dis) == 0:
                    continue  # Skip if no known faces

                match_index = np.argmin(face_dis)
                matches = face_recognition.compare_faces([known_encodings[match_index]], encode_face)

                if matches[0]:
                    name = known_names[match_index].upper()

                    # **Prevent duplicate print statements**
                    if name not in marked_names:
                        print(f"Match found: {name}")  # Print only once
                        mark_attendance(name)
                        log_info(f"Attendance marked for {name}")
                        marked_names.add(name)  # Add to the set to prevent duplicates

                    # Scale face location back to original size
                    y1, x2, y2, x1 = [v * 2 for v in face_loc]

                    # Draw rectangle and name label
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Show webcam feed
            cv2.imshow('Webcam', img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                log_info("User manually stopped the video capture.")
                break

        except Exception as e:
            log_error(f"Error during face recognition: {str(e)}")
            break

    cap.release()
    cv2.destroyAllWindows()
    log_info("Video capture ended.")
