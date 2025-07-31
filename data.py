import os
import io
import pandas as pd
import base64
import time
import tempfile
import json
import sys
from pathlib import Path
from getpass import getpass
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


DATA_FILE = "data"
SALT_SIZE = 16
SESSION_FILE = tempfile.gettempdir() + "/session"
SESSION_DURATION = 300
FIELD_NAMES = ["service", "usrname", "passwd"]
APP_NAME = "PasswordManager"

####################
## CONFIG METHODS ##
####################

def get_default_config_dir() -> Path:
    if sys.platform == "win32":
        return Path(os.getenv("APPDATA")) / APP_NAME
    else:
        return Path.home() / ".config" / APP_NAME
    
    
CONFIG_DIR = get_default_config_dir()
CONFIG_PATH = CONFIG_DIR / "config.json"

DEFAULT_DATA_FOLDER = ".dat/"

DEFAULT_CONFIG = {
    "storage_dir": DEFAULT_DATA_FOLDER,  # Default storage location inside config dir
}

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def get_data_folder() -> str:
    DATA_FOLDER = load_config()["storage_dir"] + "/"
    DATA_FOLDER = DATA_FOLDER.replace("\\", "/")  # Ensure forward slashes for compatibility
    return DATA_FOLDER

######################
## SECURITY METHODS ##
######################

def write_binary_data(data, filename: str):
    if os.path.isdir(get_data_folder()):
        with open(get_data_folder() + filename, 'wb+') as file:
            file.write(data)
    else:
        os.mkdir(get_data_folder())
        with open(get_data_folder() + filename, 'wb+') as file:
            file.write(data)

def read_binary_data(filename: str):
    try:
        with open(get_data_folder() + filename, 'rb') as file:
            dat = file.read()
            return dat
    except FileNotFoundError:
        print ('No such file %s exists' % filename)
        return b''

def get_salt():
    if os.path.exists(get_data_folder()+DATA_FILE):
        with open(get_data_folder()+DATA_FILE, "rb") as file:
            salt = file.read()[:SALT_SIZE]
            return salt
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
        # print ("loaded dem jawns")
        return Fernet(key)

    if password is None:
        raise ValueError("Password required if no session exists.")
    # print("Creating new Fernet instance with provided password.")
    key = get_key(password)
    return Fernet(key)

def is_valid(fernet):
    encrypted = read_binary_data(DATA_FILE)[SALT_SIZE:]
    try:
        fernet.decrypt(encrypted)  # Test if key is valid
        return True
    except InvalidToken:
        return False
    return False


def prompt_for_password(prompt="Master password: "):
    encrypted = read_binary_data(DATA_FILE)[SALT_SIZE:]

    while True:
        try:
            fernet = get_fernet()
            # print("Session key loaded successfully.")
            return fernet
        except ValueError:
            # print("Session key not found or invalid. Please enter the master password.")
            try:
                password = getpass(prompt).encode("utf-8")
                # print("Attempting to create Fernet instance with provided password.")
                fernet = get_fernet(password)
                if is_valid(fernet):
                    save_session_key(get_key(password))
                    return fernet
                else:
                    print("❌ Invalid password. Please try again.")
            except Exception as e:
                print(f"\n❌ Unexpected error during password entry: {e}")


def data_exists():
    return os.path.exists(get_data_folder() + DATA_FILE)

def session_exists():
    return os.path.exists(SESSION_FILE)

#######################
## DATAFRAME METHODS ##
#######################

def get_dataframe(f):
    try:
        dat = read_binary_data(DATA_FILE)
        read_dat = f.decrypt(dat[SALT_SIZE:]).decode('utf-8')
        input = io.StringIO(read_dat)
        df_read = pd.read_csv(input)
        return df_read
    except InvalidToken:
        print("Incorrect password")
        pass

    return None      
    

def write_dataframe(f, df):
    # Save to CSV in-memory using pandas
    output = io.StringIO()
    df.to_csv(output, index=False)
    csv_data = output.getvalue()

    # Encrypt and save to file
    token = f.encrypt(csv_data.encode('utf-8'))
    write_binary_data(get_salt() + token, DATA_FILE)

def create_empty_dataframe():
    # Create an empty DataFrame with the required columns
    return pd.DataFrame(columns=FIELD_NAMES)

def add_service(fernet, service: str, usrname: str, passwd: str):
    df = get_dataframe(fernet)

    row = [service, usrname, passwd]
    df = pd.concat([df, pd.DataFrame([row],
                                     columns=FIELD_NAMES)],
                   ignore_index=True)
    
    write_dataframe(fernet, df)

def remove_service(fernet, service: str):
    df = get_dataframe(fernet)

    df = df[df["service"] != service]

    write_dataframe(fernet, df)

def get_credentials(fernet, service: str):
    df = get_dataframe(fernet)
    row = df.loc[df["service"] == service]
    if not row.empty:
        return row.iloc[0]["usrname"], row.iloc[0]["passwd"]
    return None, None

def get_services(fernet):
    df = get_dataframe(fernet)

    return df["service"].unique().tolist()

#####################
## SESSION METHODS ##
#####################

def save_session_key(key: bytes):
    session_data = {
        "timestamp": time.time(),
        "key": base64.urlsafe_b64encode(key).decode()
    }
    with open(SESSION_FILE, "w") as f:
        f.write(f"{session_data['timestamp']}\n{session_data['key']}")
        

def load_session_key():
    if not os.path.exists(SESSION_FILE):
        return None

    try:
        with open(SESSION_FILE, "r") as f:
            lines = f.readlines()
            timestamp = float(lines[0].strip())
            key = base64.urlsafe_b64decode(lines[1].strip())

        if time.time() - timestamp > SESSION_DURATION:
            os.remove(SESSION_FILE)
            return None

        return key
    except:
        return None


def lock_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
