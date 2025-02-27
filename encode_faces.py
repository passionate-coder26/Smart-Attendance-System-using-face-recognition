import cv2
import face_recognition
import os
import pickle

def encode_faces(image_dir, model='hog', verbose=True):
    """Encodes faces from images in the specified directory and saves them."""
    
    encodings = []
    names = []

    if not os.path.exists(image_dir):
        print(f"Error: Directory '{image_dir}' does not exist.")
        return [], []

    for filename in os.listdir(image_dir):
        file_path = os.path.join(image_dir, filename)

        # Process only image files (ignore directories & non-image files)
        if os.path.isfile(file_path) and filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            try:
                img = cv2.imread(file_path)
                if img is None:
                    print(f"Warning: Failed to load {filename}. Skipping...")
                    continue

                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # Detect faces in the image
                boxes = face_recognition.face_locations(rgb_img, model=model)
                encs = face_recognition.face_encodings(rgb_img, boxes)

                # Extract name without extension
                name = os.path.splitext(filename)[0].split('.')[0]  # Fix double extensions

                for enc in encs:
                    encodings.append(enc)
                    names.append(name)
                    if verbose:
                        print(f"Encoded {filename} as {name}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

    return encodings, names

if __name__ == "__main__":
    image_dir = "images"  # Directory where images are stored
    encoding_file = "encodings.pkl"
    
    # Remove old encoding file to prevent duplicates
    if os.path.exists(encoding_file):
        os.remove(encoding_file)

    # Encode new faces
    new_encodings, new_names = encode_faces(image_dir, model='hog')

    if new_encodings:
        with open(encoding_file, "wb") as f:
            pickle.dump({"encodings": new_encodings, "names": new_names}, f)
        print("Encodings saved successfully.")
    else:
        print("No new valid faces found. Encoding file remains unchanged.")