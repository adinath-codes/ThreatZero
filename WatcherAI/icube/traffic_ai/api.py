from fastapi import FastAPI
from pydantic import BaseModel
from security.ml_model import TrafficML
from security.decision import decide

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