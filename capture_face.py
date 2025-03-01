import cv2
import face_recognition
import os
import sys

# Ensure the images directory exists
images_folder = "images"
os.makedirs(images_folder, exist_ok=True)

# Get student name from command-line arguments
if len(sys.argv) > 1:
    student_name = sys.argv[1]
else:
    print("Error: No username provided. Usage: python capture_face.py <username>")
    sys.exit(1)

def capture_face():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not access the camera.")
        return

    print(f"Capturing face for {student_name}. Press 'C' to capture, 'Q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image. Exiting...")
            break

        # Convert to RGB for face detection
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        # Draw rectangles around detected faces
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.putText(frame, "Press 'C' to Capture | 'Q' to Quit", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow('Capture Face', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('c') and face_locations:
            # Crop and save only the detected face
            for (top, right, bottom, left) in face_locations:
                face_image = frame[top:bottom, left:right]
                if face_image.size > 0:
                    image_path = os.path.join(images_folder, f"{student_name}.jpg")
                    cv2.imwrite(image_path, face_image)
                    print(f"✅ Face saved as {image_path}")
                    break  # Save only one face

            break  # Exit after capturing

        elif key == ord('q'):
            print("❌ Face capture canceled.")
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Face capturing completed.")

if __name__ == "__main__":
    capture_face()
