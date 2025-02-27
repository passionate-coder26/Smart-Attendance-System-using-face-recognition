import os
import encode_faces
import face_detection
from custom_logging import log_info, log_error
import pickle

if __name__ == "__main__":
    try:
        log_info("Starting the Smart Attendance System...")

        encoding_file = "encodings.pkl"
        image_dir = "images"

        # Step 1: Encode faces only if needed
        if not os.path.exists(encoding_file) or len(os.listdir(image_dir)) > 0:
            print("Encoding new faces from the images directory...")
            log_info("Encoding new faces from the images directory...")

            # Get new encodings
            new_encodings, new_names = encode_faces.encode_faces(image_dir)

            if new_encodings:
                with open(encoding_file, "wb") as f:
                    pickle.dump({"encodings": new_encodings, "names": new_names}, f)
                
                print("Encodings saved successfully.")
                log_info(f"Encoded {len(new_names)} new faces.")
            else:
                print("No new faces found. Encoding skipped.")
                log_info("No new faces found. Encoding skipped.")

        else:
            print("Encodings file already exists. Skipping encoding.")
            log_info("Encodings file already exists. Skipping encoding.")

        # Step 2: Start face detection and attendance marking
        print("Starting face detection and attendance marking...")
        log_info("Starting face detection and attendance marking...")
        face_detection.recognize_faces()
        print("Face detection and attendance marking completed.")
        log_info("Face detection and attendance marking completed.")

    except Exception as e:
        log_error(f"Error in main.py: {str(e)}")
        print(f"Error: {e}")
