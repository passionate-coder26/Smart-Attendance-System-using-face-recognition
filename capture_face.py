import cv2
import face_recognition
import os
from datetime import datetime

# Ensure the captured_faces directory exists
os.makedirs('captured_faces', exist_ok=True)

def capture_faces(max_images=5):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not access the camera.")
        return

    face_count = 0
    print("Capturing faces. Press 'q' to quit early.")

    while face_count < max_images:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image. Exiting...")
            break

        # Detect faces
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        for face_location in face_locations:
            y1, x2, y2, x1 = face_location

            # Ensure face boundaries are within the image size
            y1, y2 = max(0, y1), min(frame.shape[0], y2)
            x1, x2 = max(0, x1), min(frame.shape[1], x2)

            face_image = frame[y1:y2, x1:x2]
            
            if face_image.size > 0:  # Ensure the cropped face is not empty
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f'captured_faces/face_{timestamp}.jpg'
                cv2.imwrite(file_path, face_image)
                face_count += 1
                print(f"Face {face_count}/{max_images} saved at {file_path}")

            if face_count >= max_images:
                break

        # Draw rectangles around detected faces
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Display face count on screen
        cv2.putText(frame, f"Captured: {face_count}/{max_images}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow('Capture Faces', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Face capturing manually stopped.")
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Face capturing completed.")

if __name__ == "__main__":
    capture_faces()
