import os
import sys
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from engine_rag import EngineRAG
from pathlib import Path
# --- SETUP PATHS ---
load_dotenv(Path(__file__).parent.parent.resolve() / ".env")
API_KEY= os.getenv("GEMINI_API_KEY")
LOG_FILE = Path(__file__).parent.parent.resolve() / "logs" / "incidents.jsonl"


class ChatInfer:
    def __init__(self):
        if not API_KEY:
            print("❌ GENAI_API_KEY not found in .env")
            sys.exit(1)
        print("[-] 🤖 Initializing Chat Infer with GenAI...")
        self.rag=EngineRAG()
        self.model = "gemini-2.5-flash"
        print("[-] 🤖 Connecting to Gemini Brain...")
        self.client = genai.Client(api_key=API_KEY)
        self.system_instructions = (
            "You are InferAI, a Real-Time Cybersecurity Analyst."
            "You have access to two data sources via RAG: \n"
            "1. **Static Knowledge**: MITRE ATT&CK and CAPEC definitions.\n"
            "2. **Live Server Logs**: Real-time incidents from the 'incidents.jsonl' file.\n\n"
            "When asked about 'current threats', 'recent attacks', or specific IPs, "
            "PRIORITIZE the 'REAL-TIME LOG ENTRY' data from your context. "
            "Always cite the timestamp and IP when discussing logs."
        )
        self.chat = self.client.chats.create(
            model = self.model,
            config = types.GenerateContentConfig(
                system_instruction=self.system_instructions,
                temperature=0.2
            )
        )
    def start_chat(self):
        print("\n" + "="*60)
        print("💬 InferAI Interactive Terminal")
        print("Type 'exit' to quit, 'refresh' to reload logs.")
        print("="*60 + "\n")
        while True:
            try:
                user_input = input("Enter the prompt: ").strip()
                if user_input.lower() in ["exit", "quit"]:
                    print("Exiting InferAI. Goodbye!")
                    break
                if user_input.lower() == "refresh":
                        # print("[-] 🔄 Refreshing RAG Database...")
                        # self.rag.refresh_knowledge()
                        print("[-] 🔄 Syncing latest logs to RAG Brain...")
                        self.rag.sync_logs_only() 
                        continue
                if not user_input:
                    continue
                # 1. Retrieve Expert Knowledge
                print("(Thinking... searching knowledge base)")
                expert_context = self.rag.query(user_input,k=3)
                # 2. Construct Message
                full_prompt = (
                    f"--- USER QUERY ---\n"
                    f"{user_input}\n\n"
                    f"--- EXPERT KNOWLEDGE (RAG) ---\n"
                    f"{expert_context}\n\n"
                    f"TASK: Provide a detailed response based on the query and context."
                )
                response = self.chat.send_message(full_prompt)
                print(f"\n🤖 \033[96mInferAI:\033[0m {response.text}\n")

            except KeyboardInterrupt:
                print("\n[-] Session interrupted.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
# test chat
if __name__ == "__main__":
    infer = ChatInfer()
    infer.start_chat()