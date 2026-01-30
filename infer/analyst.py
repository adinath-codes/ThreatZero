from pathlib import Path
import time
import json
import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from engine_rag import EngineRAG
import redis


load_dotenv(Path(__file__).parent.parent.resolve() / ".env")
API_KEY= os.getenv("GEMINI_API_KEY")
LOG_FILE = Path(__file__).parent.parent.resolve() / "logs" / "incidents.jsonl"
r = redis.Redis(host='localhost', port=6379, db=0)

class SecurityAnalyst:
    def __init__(self):
        if not API_KEY:
            print("❌ GENAI_API_KEY not found in .env")
            sys.exit(1)
        print("[-] 🤖 Initializing Security Analyst with GenAI...")
        self.rag=EngineRAG()
        print("[-] 🤖 Connecting to Gemini Brain...")
        self.client = genai.Client(api_key=API_KEY)
        self.model = "gemini-2.5-flash"
        self.system_prompt = (
            "You are a Tier-3 SOC Analyst for ThreatZero. "
            "Your goal is to explain security alerts to the team clearly and quickly. "
            "You should'nt hallucinate or make up information. If unsure, say 'Insufficient data'. "
            "Use the provided RAG Context (MITRE/CAPEC) to attribute the attack and suggest fixes. "
            "Keep it brief (under 150 words). \n"
            "Format: \n"
            "🛡️ **Threat**: [Name of Attack]\n"
            "📚 **Intel**: [MITRE ID or CAPEC ID if found]\n"
            "💡 **Analysis**: [Explain what happened and the intent]\n"
            "🛠️ **Fix**: [Immediate remediation step]\n"
            "⚡ **ACTION**: [Choose one: BLOCK_IP, BLACKLIST_STRING, NONE]\n"
            "🎯 **TARGET**: [The IP address OR the specific malicious string to ban]"
        )
    def execute_self_heal(self,text,log_entry):
        """Parse Gemini's response and run it into redis"""
        lines=text.split("\n")
        action = None
        target=""
        for line in lines:
            if "⚡ **ACTION**:" in line:
                action = line.split(":", 1)[1].strip()
            if "🎯 **TARGET**:" in line:
                target = line.split(":", 1)[1].strip()
        # --- Execute Action ---
        if action == "BLOCK_IP" and target:
            print(f"[-] ⚔️ AI COMMAND: Blocking IP {target} for 24 hours.")
            r.setex(target, 86400, "banned_by_analyst") # 24 Hour Ban
        elif action == "BLACKLIST_STRING" and target:
            # Only blacklist if it's not a common word (Safety check)
            print(f"[-] ⚔️ AI COMMAND: Global Ban for payload pattern '{target}'")
            r.sadd("ai_blocked_signatures", target)

    def analyze_alert(self, log_entry):
        # 1. Retrieve Expert Knowledge
        # We query the DB for the payload or the command used
        query_text = f"{log_entry.get('payload', '')} {log_entry.get('verdict', '')} {log_entry.get('input_cmd', '')}"
        expert_context = self.rag.query(query_text)
        # 2. Construct Prompt
        user_prompt = (
            f"--- NEW INCIDENT LOG ---\n"
            f"{json.dumps(log_entry, indent=2)}\n\n"
            f"--- EXPERT KNOWLEDGE (RAG) ---\n"
            f"{expert_context}\n\n"
            f"TASK: Analyze this threat based on the logs and context."
        )
        # 3. Call Gemini API
        try:
            response = self.client.models.generate_content(
                model=self.model,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    temperature=0.3
                ),
                contents=[user_prompt]
            )
            return response.text
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            return "Error during analysis."
    def start_monitoring(self):
        print("[-] 🚨 Starting Security Analyst Monitoring...")
        # Wait for log file to exist
        while not Path(LOG_FILE).exists():
            time.sleep(1)
        with open(LOG_FILE, "r") as f:
            # Go to the end of the file (Skip old logs)
            f.seek(0, os.SEEK_END)
            
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5) 
                    continue
                
                try:
                    log_entry = json.loads(line)
                    
                    # Filter: Only analyze Threats or Honeypot Activity
                    # Adjust logic based on your exact log structure
                    is_threat = log_entry.get("verdict") in ["Malicious", "Suspicious", "Post-Compromise"]
                    is_honeypot = log_entry.get("source") in ["Honeypot", "SSH_Honeypot"]

                    if is_threat or is_honeypot:
                        print(f"\n[!] 🚨 DETECTED: {log_entry.get('event_type', 'Threat')}")
                        print("[-] ⏳ Asking Gemini + RAG...")
                        
                        briefing = self.analyze_alert(log_entry)
                        
                        print("\n" + "="*60)
                        print(briefing)
                        print("="*60 + "\n")
                        # --- EXECUTE THE AI'S DECISION ---
                        self.execute_self_heal(briefing, log_entry)
                except json.JSONDecodeError:
                    pass
# Test block
if __name__ == "__main__":
    analyst = SecurityAnalyst()
    analyst.start_monitoring()