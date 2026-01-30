from fastapi import FastAPI
from pydantic import BaseModel
from watcherAI.traffic_ai.security.ml_model import TrafficML
from watcherAI.traffic_ai.security.decision import decide

app = FastAPI()
ml = TrafficML()

class TrafficInput(BaseModel):
    payload: str

@app.post("/inspect")
def inspect(data: TrafficInput):
    text = data.payload
    ml_label, ml_conf = ml.predict(text)
    verdict = decide(text, ml_label, ml_conf)
    return {"verdict": verdict}
##verdict labels:
## 0 - Good
## 1 - sus
## 2 - Malicious