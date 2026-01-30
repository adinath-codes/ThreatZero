import pickle
import numpy as np
import os
class TrafficML:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 2. Point to the model in the parent directory (traffic_ai)
        # Path logic: security/../model.pkl
        model_path = os.path.join(current_dir, "model.pkl")
        
        # 3. Load the model safely
        print(f"[-] 🧠 Loading ML Model from: {os.path.abspath(model_path)}")
        
        with open(model_path, "rb") as f:
            self.vectorizer, self.model = pickle.load(f)

    def predict(self, text):
        X = self.vectorizer.transform([text])
        probs = self.model.predict_proba(X)[0]
        label = int(np.argmax(probs))
        confidence = float(probs[label])
        return label, confidence