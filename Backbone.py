from fastapi import FastAPI
import redis
import json

#Setup
app = FastAPI()
r= redis.Redis(host='localhost', port=6379, db=0)
logs=[]

@app.get("/")
async def read_root():
    return {"Hello": "World"}

### --- ANALYTICS ENDPOINTS ---

@app.get("/api/dashboard/stats/risks")
async def analytics_datas():
    active_bans=len(r.keys("block:*"))
    response={"risk_score":max(0,100-active_bans*5),"active_bans_count":active_bans}
    return response

@app.get("/api/dashboard/stats/logs")
async def analytics_table():
    with open("logs/incidents.jsonl","r") as lines:
        for line in lines:
            logs.append(json.load(line.strip()))
    print(logs)
    return logs  

# ipinfo : https://geolocation-db.com/json/3aad2710-83de-11f0-9ca8-69fb6dc92fe1/127.0.0.1

### --- LIVE ANALYSIS ENDPOINTS ---

@app.get("/inferai/live")
async def inferai_live():
    return {"status": "Inference endpoint is live"}

### --- CHAT ENDPOINTS ---
@app.post("/inferai/chat")
async def inferai_chat(message:str):
    return {"response": f"Received your message: {message}"}
@app.get("/inferai/chat/refresh")
async def inferai_chat_refresh():
    return {"response": "Refresh endpoint called"}