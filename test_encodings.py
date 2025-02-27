import pickle

# Load encodings.pkl
try:
    with open("encodings.pkl", "rb") as f:
        data = pickle.load(f)
    
    print("Saved Names:", data["names"])
    print("Total Encodings:", len(data["encodings"]))

except Exception as e:
    print(f"Error loading encodings.pkl: {e}")
