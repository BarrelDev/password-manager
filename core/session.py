#####################
## SESSION METHODS ##
#####################

import base64
import time
import tempfile
import os
import json

SESSION_FILE = os.path.join(tempfile.gettempdir(), "session")
SESSION_DURATION = 300 # seconds

def save_session_key(key: bytes):
    session_data = {
        "timestamp": time.time(),
        "key": base64.urlsafe_b64encode(key).decode()
    }
    with open(SESSION_FILE, "w") as f:
        json.dump(session_data, f)
        

def load_session_key() -> bytes | None:
    if not os.path.exists(SESSION_FILE):
        return None

    try:
        with open(SESSION_FILE, "r") as f:
            session_data = json.load(f)

        timestamp = float(session_data["timestamp"])
        encoded_key = session_data["key"]

        if time.time() - timestamp > SESSION_DURATION:
            lock_session()
            return None

        return base64.urlsafe_b64decode(encoded_key)
    except (ValueError, KeyError, json.JSONDecodeError):
        return None


def lock_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

def is_session_valid() -> bool:
    key = load_session_key()
    return key is not None