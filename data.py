import os
import io
import pandas as pd
import base64
import time
import tempfile
from timeout import getpass_timeout
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

DATA_FOLDER = ".dat/"
DATA_FILE = "data"
SALT_FILE = "salt"
SESSION_FILE = tempfile.gettempdir() + "/session"
SESSION_DURATION = 300
FIELD_NAMES = ["service", "usrname", "passwd"]

######################
## SECURITY METHODS ##
######################

def write_binary_data(data, filename: str):
    if os.path.isdir(DATA_FOLDER):
        with open(DATA_FOLDER + filename, 'wb+') as file:
            file.write(data)
    else:
        os.mkdir(DATA_FOLDER)
        with open(DATA_FOLDER + filename, 'wb+') as file:
            file.write(data)

def read_binary_data(filename: str):
    try:
        with open(DATA_FOLDER + filename, 'rb') as file:
            dat = file.read()
            return dat
    except FileNotFoundError:
        print ('No such file %s exists' % filename)
        return b''

def get_salt():
    if os.path.exists(DATA_FOLDER+SALT_FILE):
        with open(DATA_FOLDER+SALT_FILE, "rb") as file:
            salt = file.read()
            return salt
    else:
        salt = os.urandom(16)
        write_binary_data(salt, SALT_FILE)
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
    encrypted = read_binary_data(DATA_FILE)
    try:
        fernet.decrypt(encrypted)  # Test if key is valid
        return True
    except InvalidToken:
        return False
    return False


def prompt_for_password(prompt="Master password: ", timeout=60):
    encrypted = read_binary_data(DATA_FILE)

    while True:
        try:
            fernet = get_fernet()
            # print("Session key loaded successfully.")
            return fernet
        except ValueError:
            # print("Session key not found or invalid. Please enter the master password.")
            try:
                password = getpass_timeout(prompt, timeout=timeout).encode("utf-8")
                # print("Attempting to create Fernet instance with provided password.")
                fernet = get_fernet(password)
                if is_valid(fernet):
                    save_session_key(get_key(password))
                    return fernet
                else:
                    print("❌ Invalid password. Please try again.")
            except TimeoutError as e:
                print(f"\n{e}")
            except Exception as e:
                print(f"\n❌ Unexpected error during password entry: {e}")


def data_exists():
    return os.path.exists(DATA_FOLDER + DATA_FILE)

def session_exists():
    return os.path.exists(SESSION_FILE)

#######################
## DATAFRAME METHODS ##
#######################

def get_dataframe(f):
    try:
        read_dat = f.decrypt(read_binary_data(DATA_FILE)).decode('utf-8')
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
    write_binary_data(token, DATA_FILE)

def create_empty_dataframe():
    # Create an empty DataFrame with the required columns
    return pd.DataFrame(columns=FIELD_NAMES)

def add_service(fernet, service: str, usrname: str, passwd: str):
    df = get_dataframe(fernet)
   
    #Remove old credentials if service already exists.
    df = df[df["service"] != service]

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
