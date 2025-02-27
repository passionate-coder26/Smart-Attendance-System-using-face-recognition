import encode_faces
import face_detection
from attendance import update_attendance

if __name__ == "__main__":
    # Step 1: Encode faces from the images directory
    print("Encoding faces from the images directory...")
    encode_faces.encode_faces("images")
    print("Face encoding completed.")

    # Step 2: Start face detection and attendance marking
    print("Starting face detection and attendance marking...")
    face_detection.recognize_faces()
    print("Face detection and attendance marking completed.")

    # Step 3: Update the attendance file after processing
    update_attendance()
    print("Attendance file updated.")