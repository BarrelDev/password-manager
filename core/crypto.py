import os
import base64

from getpass import getpass
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from core.binary import read_binary_data, write_binary_data
from core.config import get_data_folder
from core.session import is_session_valid, save_session_key, load_session_key

SALT_SIZE = 16
DATA_FILE = "data"

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

def get_data_file(fernet: Fernet) -> bytes | None:
    try:
        dat = read_binary_data(DATA_FILE)
        read_dat = fernet.decrypt(dat[SALT_SIZE:]).decode('utf-8')
        return read_dat
    except InvalidToken:
        print("Invalid password")
        return None
    except FileNotFoundError:
        print(f"No such file {DATA_FILE} exists")
        return None
    
def write_data_file(fernet: Fernet, data: str):
    token = fernet.encrypt(data.encode('utf-8'))
    write_binary_data(get_salt() + token, DATA_FILE)

def prompt_for_password(prompt="Master password: "):
    encrypted = read_binary_data(DATA_FILE)[SALT_SIZE:]

    if is_session_valid():
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
