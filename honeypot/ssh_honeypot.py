# Import library dependencies.
import logging
import paramiko
import threading
import socket
import time
import sys
import os
from pathlib import Path

# --- SETUP PATHS & LOGGER ---
# Ensure we can import logger_config from the parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from logger_config import setup_logger
    from honeypot.os_honey import FakeTerminal
except ImportError:
    # Fallback if running from root
    from os_honey import FakeTerminal
    from logger_config import setup_logger

# Initialize the Unified JSON Logger
logger = setup_logger("SSHHoneypot")

# Constants
SSH_BANNER = "SSH-2.0-MySSHServer_1.0"
BASE_DIR = Path(__file__).parent.parent.resolve()
SERVER_KEY = os.path.join(current_dir, 'server.key') # improved path handling

# Generate key if missing (Prevents startup crash)
if not os.path.exists(SERVER_KEY):
    print("[-] Generating temporary RSA host key...")
    key = paramiko.RSAKey.generate(2048)
    key.write_private_key_file(SERVER_KEY)

host_key = paramiko.RSAKey(filename=SERVER_KEY)

# SSH Server Class
class Server(paramiko.ServerInterface):

    def __init__(self, client_ip, input_username=None, input_password=None):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
    
    def get_allowed_auths(self, username):
        return "password"

    def check_auth_password(self, username, password):
        # --- LOGGING LOGIN ATTEMPTS FOR RAG ---
        auth_status = "Failed"
        if self.input_username and self.input_password:
            if username == self.input_username and password == self.input_password:
                auth_status = "Successful"
        else:
            auth_status = "Successful" # Honeypot mode (accept all)

        log_details = {
            "event_type": "auth_attempt",
            "source": "SSH_Honeypot",
            "attacker_ip": self.client_ip,
            "username": username,
            "password": password,
            "status": auth_status
        }
        
        # Log to JSONL
        logger.info(f"SSH Auth {auth_status} for {username} from {self.client_ip}", extra={"details": log_details})

        if auth_status == "Successful":
            return paramiko.AUTH_SUCCESSFUL
        else:
            return paramiko.AUTH_FAILED
    
    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_exec_request(self, channel, command):
        command = str(command)
        return True

def emulated_shell(channel, client_ip):
    # Initialize the Fake OS
    term = FakeTerminal()
    
    channel.send(b"Welcome to Ubuntu 22.04 LTS\r\n")
    channel.send(term.get_prompt().encode())
    
    command = b""
    while True:
        try:
            char = channel.recv(1)
            
            if not char:
                channel.close()
                break
            
            # --- DEBUGGING: See what the client is actually sending ---
            # This will show up in your server terminal, not the client's
            print(f"DEBUG: Received char code: {ord(char)}") 

            # Echo back to user (so they see what they type)
            # EXCEPTION: Do not echo \r or \n immediately, handle formatting below
            if char != b"\r" and char != b"\n":
                channel.send(char)
            
            # Buffer the character (unless it's a newline)
            if char != b"\r" and char != b"\n":
                command += char
            
            # --- ENTER KEY DETECTION (Handle \r AND \n) ---
            if char == b"\r" or char == b"\n":
                # Send a clean new line to the user so visual formatting looks right
                channel.send(b"\r\n")

                cmd_str = command.strip().decode("utf-8", errors="ignore")
                
                # Avoid processing empty commands (fixes double-enter bug)
                if not cmd_str:
                    channel.send(term.get_prompt().encode())
                    command = b""
                    continue

                # --- LOGGING COMMANDS ---
                print(f"DEBUG: Processing command: '{cmd_str}'") # Debug print

                # 1. Get Response from Fake OS
                output = term.run_command(cmd_str)
                
                # 2. Log the Interaction
                log_details = {
                    "event_type": "command_execution",
                    "source": "SSH_Honeypot",
                    "attacker_ip": client_ip,
                    "input_cmd": cmd_str,
                    "system_response_snippet": output[:100], 
                    "session_id": str(id(channel)) 
                }
                logger.info(f"CMD: {cmd_str}", extra={"details": log_details})

                # Handle Special Exit Commands
                if cmd_str in ["exit", "quit", "logout"]:
                    channel.send(b"logout\r\n")
                    channel.send(b"Connection to localhost closed.\r\n")
                    channel.close()
                    break
                
                # Handle "Hidden" commands (Easter Eggs)
                if cmd_str == "fuckyou":
                     channel.send(b"Permission denied: Watch your language.\r\n")
                     channel.send(term.get_prompt().encode())
                     command = b""
                     continue

                # 3. Send Output to User
                # Format: Newline -> Output -> Newline -> Prompt
                response = output.encode() + b"\r\n"
                channel.send(response)
                channel.send(term.get_prompt().encode())
                
                # Reset Buffer
                command = b""

        except Exception as e:
            logger.error(f"Shell Error: {e}")
            print(f"CRITICAL SHELL ERROR: {e}") # Print to terminal to see crashes
            break
def client_handle(client, addr, username, password, tarpit=False):
    client_ip = addr[0]
    print(f"[-] New Connection: {client_ip}")
    
    try:
        transport = paramiko.Transport(client)
        transport.local_version = SSH_BANNER
        
        server = Server(client_ip=client_ip, input_username=username, input_password=password)
        
        # Load host key safely
        try:
            transport.add_server_key(host_key)
        except Exception as e:
            print(f"❌ Error loading host key: {e}")
            return

        transport.start_server(server=server)

        channel = transport.accept(20) # Wait 20s for auth
        if channel is None:
            return

        standard_banner = "Welcome to Ubuntu 22.04 LTS (Jammy Jellyfish)!\r\n\r\n"
        
        try:
            if tarpit:
                endless_banner = standard_banner * 100
                for char in endless_banner:
                    channel.send(char)
                    time.sleep(8)
            else:
                channel.send(standard_banner)
                emulated_shell(channel, client_ip=client_ip)

        except Exception as error:
            print(f"Session Error: {error}")

    except Exception as error:
        print(f"Transport Error: {error}")
    
    finally:
        try:
            transport.close()
        except:
            pass
        client.close()

def honeypot(address, port, username, password, tarpit=False):
    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        socks.bind((address, port))
    except PermissionError:
        print(f"❌ Error: Permission denied binding to port {port}. Try using 'sudo' or port 2222.")
        return

    socks.listen(100)
    print(f"[-] 🛡️ SSH Honeypot Active on {address}:{port}")
    logger.info(f"SSH Honeypot Started on {address}:{port}")

    while True: 
        try:
            client, addr = socks.accept()
            ssh_honeypot_thread = threading.Thread(target=client_handle, args=(client, addr, username, password, tarpit))
            ssh_honeypot_thread.daemon = True # Kills thread if main program exits
            ssh_honeypot_thread.start()
        except Exception as error:
            print(f"Error accepting client: {error}")

# Example usage if run directly
# if __name__ == "__main__":
#     # Ensure server.key exists for standalone testing
#     if not os.path.exists(SERVER_KEY):
#         paramiko.RSAKey.generate(2048).write_private_key_file(SERVER_KEY)
#     honeypot('0.0.0.0', 2222, 'root', 'toor')