import logging
import json
import os
import time
from pathlib import Path 
# Create logs directory if it doesn't exist

DIR = Path(__file__).parent.resolve()
LOG_DIR = DIR / 'logs'
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "incidents.jsonl")

class JsonFormatter(logging.Formatter):
    """
    Formatter that dumps the log record as a JSON object.
    """
    def format(self, record):
        log_record = {
            "timestamp": time.time(),
            "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created)),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        # Merge extra fields passed in the logging call
        if hasattr(record, "details"):
            log_record.update(record.details)
        
        return json.dumps(log_record)

def setup_logger(name="ThreatZeroLogger"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid adding handlers multiple times if imported in multiple files
    if not logger.handlers:
        # File Handler (Writes to incidents.jsonl)
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)

        # Stream Handler (Optional: Also print simple alerts to terminal)
        stream_handler = logging.StreamHandler()
        # Simple format for terminal, JSON for file
        stream_handler.setFormatter(logging.Formatter('[-] %(message)s'))
        logger.addHandler(stream_handler)

    return logger