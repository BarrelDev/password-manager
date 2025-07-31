import os
import base64

from getpass import getpass
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from core.data import get_data_folder, read_binary_data, write_binary_data
from core.data import DATA_FILE, SALT_SIZE
from core.session import save_session_key, load_session_key, SESSION_FILE

def get_salt():
    path = os.path.join(get_data_folder(), DATA_FILE)
    if os.path.exists(path):
        return read_binary_data(DATA_FILE)[:SALT_SIZE]
    else:
        salt = os.urandom(SALT_SIZE)
        write_binary_data(salt, DATA_FILE)
        return salt

def get_key(password):
    salt = get_salt()

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1_200_000,
    )

    key = base64.urlsafe_b64encode(kdf.derive(password))

    return key

def get_fernet(password=None):
    key = load_session_key()
    
    if key:
        return Fernet(key)

    if password is None:
        raise ValueError("Password required if no session exists.")
    
    key = get_key(password)
    return Fernet(key)

def is_valid(fernet):
    encrypted = read_binary_data(DATA_FILE)

    if not encrypted or len(encrypted) <= SALT_SIZE:
        return False

    try:
        fernet.decrypt(encrypted[SALT_SIZE:])  # Test if key is valid
        return True
    except InvalidToken:
        return False


def prompt_for_password(prompt="Master password: "):
    encrypted = read_binary_data(DATA_FILE)[SALT_SIZE:]

    if session_exists():
        try:
            return get_fernet()
        except Exception:
            pass

    while True:
        try:
            password = getpass(prompt).encode("utf-8")
            
            fernet = get_fernet(password)
            if is_valid(fernet):
                save_session_key(get_key(password))
                return fernet
            else:
                print("❌ Invalid password. Please try again.")
        except Exception as e:
            print(f"\n❌ Unexpected error during password entry: {e}")


def data_exists():
    path = os.path.join(get_data_folder(), DATA_FILE)
    return os.path.exists(path)

def session_exists():
    return os.path.exists(SESSION_FILE)
