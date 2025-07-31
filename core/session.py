#####################
## SESSION METHODS ##
#####################

import base64
import time
import keyring

SESSION_SERVICE = "password_manager_session"
SESSION_USER = "session_key"
SESSION_DURATION = 300 # seconds

def save_session_key(key: bytes):
    session_data = f"{time.time()}|{base64.urlsafe_b64encode(key).decode('utf-8')}"
    keyring.set_password(SESSION_SERVICE, SESSION_USER, session_data)
        

def load_session_key() -> bytes | None:
    session_data = keyring.get_password(SESSION_SERVICE, SESSION_USER)
    if not session_data:
        return None
    try:
        timestamp_str, key_str = session_data.split("|")
        timestamp = float(timestamp_str)
        if time.time() - timestamp > SESSION_DURATION:
            lock_session()
            return None
        return base64.urlsafe_b64decode(key_str.encode())
    except Exception:
        return None


def lock_session():
    try:
        keyring.delete_password(SESSION_SERVICE, SESSION_USER)
    except keyring.errors.PasswordDeleteError:
        pass # No session stored

def is_session_valid() -> bool:
    key = load_session_key()
    return key is not None