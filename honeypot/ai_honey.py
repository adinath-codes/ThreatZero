import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

class HoneyGenAI:
    def __init__(self):
        load_dotenv()
        self.API_KEY = os.getenv("GEMINI_API_KEY")
        
        if not self.API_KEY:
            raise ValueError("GEMINI_API_KEY not set in environment variables.")

        # 1. Initialize the Client (New SDK Style)
        self.client = genai.Client(api_key=self.API_KEY)

        # 2. Define System Instructions using the 'types' object
        system_prompt = (
            "You are a vulnerable Ubuntu 22.04 LTS Linux server. "
            "The user is a hacker who has gained unauthorized access. "
            "Your goal is to be a perfect decoy. "
            "ONLY output the exact text a terminal would show. "
            "Do not include conversational AI filler like 'Sure, here is the output'. "
            "If they type 'ls', show a fake list of files including 'passwords.txt' and 'config.php'. "
            "If they type 'cat passwords.txt', show fake credentials. "
            "Maintain a consistent state."
            "You are a sophisticated 'Honeypot' simulating a vulnerable server environment. "
            "Your job is to keep the attacker engaged by returning realistic outputs for their attacks. "
            
            "RULES:"
            "1. IF input is a Linux Command (e.g., 'ls', 'whoami', 'cat', 'wget'): "
            "   - Act as an Ubuntu 22.04 terminal. Output ONLY the shell response."
            "   - Include fake files like 'passwords.txt', 'database.sql', and 'config.php'."
            
            "2. IF input is an SQL Injection (e.g., 'UNION SELECT', 'OR 1=1', 'id=1'): "
            "   - Act as a compromised MySQL database."
            "   - Output a realistic table dump or query result."
            "   - Do NOT say 'bash: command not found'. Pretend the injection succeeded."
            "   - For 'information_schema', list tables like 'users', 'admin_logs', 'payments'."
            
            "3. GENERAL: "
            "   - Be concise. No explanations. No 'Here is the output'."
            "   - Maintain state where possible."
        )

        # 3. Create the Chat Session
        self.chat = self.client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1  # Low temperature makes output more deterministic/robotic
            )
        )

    def get_response(self, command: str) -> str:
        try:
            print(f"[-] 🐝 HoneyGenAI Sending Command to AI Brain: {command}")
            response = self.chat.send_message(command)
            print(f"[-] 🐝 HoneyGenAI Received Response: {response.text}")
            return response.text
        except Exception as e:
            return f"Error communicating with AI Brain: {e}"
        
        except Exception as e:
            print(f"Startup Error: {e}")

# --- Usage Example ---
# if __name__ == "__main__":
#     try:
#         honeyAI = HoneyGenAI()
        
#         # Test a command
#         print("[-] Sending 'cat >> btihv.txt' to HoneyGenAI...")
#         output = honeyAI.get_response("cat >> btihv.txt")
#         print(output)        
            
#     except Exception as e:
#         print(f"Startup Error: {e}")