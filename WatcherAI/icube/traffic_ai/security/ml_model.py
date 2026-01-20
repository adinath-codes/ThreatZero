import pickle
import numpy as np

class TrafficML:
    def __init__(self):
        with open("model.pkl", "rb") as f:
            self.vectorizer, self.model = pickle.load(f)

    def predict(self, text):
        X = self.vectorizer.transform([text])
        probs = self.model.predict_proba(X)[0]
        label = int(np.argmax(probs))
        confidence = float(probs[label])
        return label, confidence