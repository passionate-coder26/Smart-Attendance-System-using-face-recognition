import cv2
import face_recognition
import os

# Ensure the captured_faces directory exists
os.makedirs('captured_faces', exist_ok=True)

def capture_faces(max_images=5):
    cap = cv2.VideoCapture(0)
    face_count = 0
    print("Capturing faces. The program will stop after capturing 5 faces.")

    while face_count < max_images:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image. Exiting...")
            break
        
        # Detect faces in the frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        
        for face_location in face_locations:
            y1, x2, y2, x1 = face_location
            face_image = frame[y1:y2, x1:x2]
            file_path = f'captured_faces/face_{face_count}.jpg'
            cv2.imwrite(file_path, face_image)
            face_count += 1
            print(f"Face {face_count} saved at {file_path}")
            if face_count >= max_images:
                break
        
        # Draw rectangles around detected faces
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        
        cv2.imshow('Capture Faces', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Face capturing completed.")

if __name__ == "__main__":
    capture_faces()
