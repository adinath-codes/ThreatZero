import os
import pandas as pd

class DatasetRuleEngine:
    def __init__(self):
                # 1. Get the directory where THIS script (llm_outsider.py) lives
        # Result: .../WatcherAI/traffic_ai/security
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # 2. Go UP one folder (to traffic_ai), then INTO 'dataset'
        # Path logic: security/../dataset/traffic_dataset.csv
        csv_path = os.path.join(base_dir, "../dataset/traffic_dataset.csv")
        
        # 3. Resolve to an absolute path (removes the '..')
        path = os.path.abspath(csv_path)

        print(f"[-] 📊 Loading Dataset from: {path}")
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