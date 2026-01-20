import pandas as pd

class LLMOutsider:
    def __init__(self, path="dataset/traffic_dataset.csv"):
        df = pd.read_csv(path)
        self.context = df[df["label"] == 2]["text"].astype(str).tolist()

    def analyze(self, text):
        for sample in self.context:
            if any(word in text.lower() for word in sample.lower().split()):
                return 2
        return 0