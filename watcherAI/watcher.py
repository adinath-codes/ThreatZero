import sys
import os
import httpx
import asyncio
import redis
from fastapi import FastAPI, Request, Response
from starlette.background import BackgroundTask
from pathlib import Path
# --- IMPORTS (Adjust based on your structure) ---
from honeypot.os_honey import FakeTerminal
from watcherAI.traffic_ai.security.decision import decide
from watcherAI.traffic_ai.security.ml_model import TrafficML
from logger_config import setup_logger
# Setup
app = FastAPI()
web_terminal = FakeTerminal()
ml = TrafficML()
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True) # decode_responses=True ensures we get Strings back, not Bytes
logger = setup_logger("WatcherAI")
# Constants
REAL_SERVER_URL = "http://localhost:3000"
BASE_DIR = Path(__file__).parent.parent.resolve()
LOG_DIR = BASE_DIR / 'log'

def check_malicious_command(payload: str):
    """
    Parses the HTTP body/query to find injected shell commands.
    """
    if not payload: return False, None

    # 1. ML Prediction
    ml_label, ml_conf = ml.predict(payload)
    verdict = decide(payload, ml_label, ml_conf)
    
    print(f"[-] 👁️ Watcher AI Verdict: {verdict} (ML Label: {ml_label}, Confidence: {ml_conf})")

    # 2. Decision Logic
    if verdict in [1, 2]: # Suspicious or Malicious
        print(f"[!] Extracted Command: {payload}")
        return True, payload
    else: 
        return False, None

def check_ai_signature(payload:str):
    """
    Placeholder for future AI rule-based checks.
    Currently not implemented.
    """
    bad_signnature = r.get("ai_bad_signature")
    if not bad_signnature:
        return False
    for sign in bad_signnature:
        sign_str = sign.decode('utf-8')
        if sign_str in payload:
            print(f"[-] 🤖 AI-Rule Match: Payload contains '{sign_str}'")
            return True
    return False
    

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def reverse_proxy(request: Request, path: str):
    client_ip = request.client.host

    # --- 1. DEFENDER LOGIC -> CHECK REDIS BLOCKLIST ---
    # Redis returns the value or None. Since it's string, checking `if val` works.
    if r.get(client_ip):
        print(f"[-] 🚫 BLOCKED REQUEST from {client_ip}")
        logger.info(f"🚫 Blocked Request from {client_ip}", extra={
            "source": "Watcher",
            "attacker_ip": client_ip,
            "verdict": "Blocked",
            "action_taken": "IP Blocked by Redis"
        })
        return Response(content="⛔ ACCESS DENIED: Threat Zero Active Defense. Your IP is blocked", status_code=403)
    print(f"[-] 👁️ Analyzing Request from {client_ip}...")
    
    # Gather ALL inputs (Body + Query Params)
    body_bytes = await request.body()
    body_str = body_bytes.decode('utf-8', errors='ignore')
    query_str = str(request.query_params) # e.g. "q=invoice&id=1"
    
    # Combine them for the AI to check
    full_payload = f"{body_str} {query_str}"
    # --- 2. AI SIGNATURE CHECK ---
    if check_ai_signature(full_payload):
        r.setex(client_ip, 3600, "blocked")
        print(f"[-] 🚫 BLOCKED REQUEST from {client_ip} due to AI Signature Match")
        logger.info(f"🚫 Blocked Request from {client_ip} due to AI Signature Match", extra={
            "source": "Watcher",
            "attacker_ip": client_ip,
            "verdict": "Blocked",
            "action_taken": "Blocked by AI Signature"
        })
        return Response(content="⛔ ACCESS DENIED: Threat Zero Active Defense. Your IP is blocked", status_code=403)
    
    is_threat, mal_cmd = check_malicious_command(full_payload)

    # --- 3. WATCHER AI -> ANALYZE TRAFFIC ---
    if is_threat:
        print(f"[-] 🚨 BLOCKING THREAT IP! -> Sending to Honeypot...")
        
        log_details = {
            "source": "Watcher",
            "attacker_ip": client_ip,
            "payload": mal_cmd,
            "verdict": "Malicious",
            "action_taken": "Redirected to Honeypot",
            "http_method": request.method,
            "url_path": str(request.url),
            "user_agent": request.headers.get("user-agent", "Unknown")
        }
        
        logger.info(f"🚨 Threat Detected from {client_ip}", extra={"details": log_details})
        
        r.setex(client_ip, 3600, "blocked")
        fake_response = web_terminal.run_command(mal_cmd or "help")
        html_response = f"<pre>{fake_response}</pre>"
        return Response(content=html_response, media_type="text/html")
        
    # --- 4. NORMAL TRAFFIC -> FORWARD TO REAL SERVER ---
    async with httpx.AsyncClient() as client:
        try:
            proxied_request = client.build_request(
                method=request.method,
                url=f"{REAL_SERVER_URL}/{path}",
                headers=request.headers.raw,
                content=body_bytes, # Send original bytes
                params=request.query_params
            )
            proxied_response = await client.send(proxied_request, stream=True)
            
            return Response(
                content=await proxied_response.aread(),
                status_code=proxied_response.status_code,
                headers=dict(proxied_response.headers)
            )
        except httpx.ConnectError:
            return Response("❌ Real Server (Port 3000) is Down!", status_code=502)