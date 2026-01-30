import os
import pandas as pd

class LLMOutsider:
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
        self.context = df[df["label"] == 2]["text"].astype(str).tolist()

    def analyze(self, text):
        for sample in self.context:
            if any(word in text.lower() for word in sample.lower().split()):
                return 2
        return 0