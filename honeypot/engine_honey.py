# honeypy.py (The Master Launcher)
import argparse
import uvicorn
import threading
from ssh_honeypot import honeypot 
import sys
import os

# --- PATH HACK: Allow importing from parent/sibling folders ---
# 1. Get the path of the current folder (honeypot)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Get the path of the parent folder (ThreatZero)
parent_dir = os.path.dirname(current_dir)

# 3. Add the parent folder to the system path
sys.path.append(parent_dir)

# --- NOW IMPORT NORMALLY ---
# Python can now "see" the 'WatcherAI' folder inside 'ThreatZero'
try:
    from watcherAI.watcher import app as watcher_app
except ImportError as e:
    print(f"❌ Error importing Watcher: {e}")
    print(f"   Looking in: {parent_dir}")
    sys.exit(1)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Threat Zero: Active Defense Launcher") 
    parser.add_argument('-a','--address', type=str, default="0.0.0.0", help="Host address")
    parser.add_argument('-p','--port', type=int, help="Port to bind to")
    parser.add_argument('-u', '--username', type=str, help="Trap Username")
    parser.add_argument('-w', '--password', type=str, help="Trap Password")
    
    # Mode selection
    parser.add_argument('-s', '--ssh', action="store_true", help="Run SSH Honeypot")
    parser.add_argument('-wh', '--http', action="store_true", help="Run Watcher AI (HTTP Proxy)")
    
    args = parser.parse_args()
    
    try:
        # 1. LAUNCH SSH HONEYPOT
        if args.ssh:
            print(f"[-] 🛡️ Starting SSH Honeypot on {args.address}:{args.port or 2222}...")
            port = args.port if args.port else 2222
            honeypot(args.address, port, args.username, args.password)
         
        # 2. LAUNCH WATCHER AI (WEB PROXY)
        elif args.http:
            print(f"[-] 👁️ Starting Watcher AI (HTTP) on {args.address}:{args.port or 8000}...")
            port = args.port if args.port else 8000
            uvicorn.run(watcher_app, host=args.address, port=port)
            
        else:
            print("Please specify a mode: --ssh or --http")

    except KeyboardInterrupt:
        print("\n[!] Stopping Threat Zero Defense System.")