import cv2
import face_recognition
import pickle
import numpy as np
from attendance import mark_attendance, update_attendance
from custom_logging import log_info, log_error

# Load known face encodings
try:
    with open("encodings.pkl", "rb") as f:
        data = pickle.load(f)
    log_info("Successfully loaded face encodings.")
    print("Loaded names:", data["names"])  # Debugging print
except Exception as e:
    log_error(f"Error loading encodings.pkl: {str(e)}")

# Set to keep track of names already marked as present
marked_names = set()

def recognize_faces():
    cap = cv2.VideoCapture(0)
    log_info("Started video capture.")
    
    while True:
        try:
            success, img = cap.read()
            if not success:
                log_error("Failed to capture frame from webcam.")
                break
            
            img_small = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            img_small_rgb = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)

            faces_cur_frame = face_recognition.face_locations(img_small_rgb)
            encodes_cur_frame = face_recognition.face_encodings(img_small_rgb, faces_cur_frame)

            for encode_face, face_loc in zip(encodes_cur_frame, faces_cur_frame):
                matches = face_recognition.compare_faces(data["encodings"], encode_face)
                face_dis = face_recognition.face_distance(data["encodings"], encode_face)
                match_index = np.argmin(face_dis)

                if matches[match_index]:
                    name = data["names"][match_index].upper()
                    print(f"Match found: {name}")  # Debugging print
                    y1, x2, y2, x1 = face_loc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    
                    # Draw rectangle around the face continuously
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    
                    # Mark attendance only once
                    if name not in marked_names:
                        mark_attendance(name)
                        log_info(f"Attendance marked for {name}")
                        marked_names.add(name)

            cv2.imshow('Webcam', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            log_error(f"Error during face recognition: {str(e)}")
            break

    cap.release()
    cv2.destroyAllWindows()
    log_info("Video capture ended.")

    # Update attendance file after processing
    update_attendance()
    log_info("Attendance file updated.")

if __name__ == "__main__":
    recognize_faces()
