import cv2
import face_recognition
import os
import pickle

def encode_faces(image_dir):
    encodings = []
    names = []

    # Ensure the directory exists
    if not os.path.exists(image_dir):
        print(f"Error: Directory '{image_dir}' does not exist.")
        return [], []

    for filename in os.listdir(image_dir):
        file_path = os.path.join(image_dir, filename)

        # Process only image files (ignore directories & non-image files)
        if os.path.isfile(file_path) and filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            img = cv2.imread(file_path)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Detect faces in the image
            boxes = face_recognition.face_locations(rgb_img, model='hog')
            encs = face_recognition.face_encodings(rgb_img, boxes)

            # Extract only the name (remove extensions)
            name = os.path.splitext(os.path.splitext(filename)[0])[0]  # Fix double extensions

            for enc in encs:
                encodings.append(enc)
                names.append(name)
                print(f"Encoded {filename} as {name}")  # Debugging print

    return encodings, names

if __name__ == "__main__":
    image_dir = "images"  # Directory where your images are stored

    # Delete existing encodings.pkl to prevent old data from being used
    if os.path.exists("encodings.pkl"):
        os.remove("encodings.pkl")
        print("Old encodings.pkl deleted.")

    encodings, names = encode_faces(image_dir)
    
    # Save new encodings
    if encodings:
        data = {"encodings": encodings, "names": names}
        with open("encodings.pkl", "wb") as f:
            pickle.dump(data, f)
        print("Encoding Complete")
    else:
        print("No valid faces found. Encoding file not created.")
