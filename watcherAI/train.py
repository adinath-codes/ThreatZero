import os
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from datasets import load_dataset
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "/security/model.pkl")
print(f"[-] 🧠 Saving ML Model to: {os.path.abspath(model_path)}")
dataset=load_dataset("YangYang-Research/web-attack-detection", split="train")
df = pd.DataFrame(dataset)

X = df["Sentence"].astype(str)
y = df["Label"]

vectorizer = TfidfVectorizer(
    max_features=10000,
    ngram_range=(1,2)
)

X_vec = vectorizer.fit_transform(X)

model = LogisticRegression(
    multi_class="auto",
    max_iter=1000
)

model.fit(X_vec, y)

with open(model_path, "wb") as f:
    pickle.dump((vectorizer, model), f)

print("MODEL TRAINED")