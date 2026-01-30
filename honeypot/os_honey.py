import datetime
from ai_honey import HoneyGenAI
from logger_config import setup_logger

#setup
logger = setup_logger("Honeypot")
class FakeTerminal:
    def __init__(self):
        self.cwd = "/usr/local"
        self.user = "corpuser1"
        self.hostname = "corporate-jumpbox2"
        self.start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.honeyAI = HoneyGenAI()

    def get_prompt(self):
        return f"{self.user}@{self.hostname}:{self.cwd}$ "

    def run_command(self, command_str):
        """
        Takes a string command (e.g., 'ls') and returns the fake output.
        """
        cmd = command_str.strip()
        response = ""
        print(f"[-] 🐝 HoneyGenAI Processing Command: {cmd}")
        if not cmd:
            response = ""
        match cmd:
            case "pwd":
                response= f"{self.cwd}\n"
            case "whoami":
                response= f"{self.user}\n"
            case "id":
                response= f"uid=1001({self.user}) gid=1001({self.user}) groups=1001({self.user})\n"
            case "uptime":
                response= f" {datetime.datetime.now().strftime('%H:%M:%S')} up 14 days,  2:14,  1 user,  load average: 0.00, 0.01, 0.05\n"
            case _:
                response= self.honeyAI.get_response(cmd)
        # Construct Log Details
        log_details = {
            "source": "Honeypot",
            "attacker_ip": "Unknown", # Or pass it in if available
            "payload": cmd,
            "verdict": "Post-Compromise",
            "action_taken": "Executed Fake Command",
            "system_response": response[:50] # Log first 50 chars only
        }

        # LOG IT
        logger.info(f"🐝 Honeypot command executed: {cmd}", extra={"details": log_details})
        return response