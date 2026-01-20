import pandas as pd

class DatasetRuleEngine:
    def __init__(self, path="dataset/traffic_dataset.csv"):
        df = pd.read_csv(path)
        self.malicious = df[df["label"] == 2]["text"].astype(str).tolist()
        self.suspicious = df[df["label"] == 1]["text"].astype(str).tolist()

    def check(self, text):
        for t in self.malicious:
            if t.lower() in text.lower():
                return 2
        for t in self.suspicious:
            if t.lower() in text.lower():
                return 1
        return 0