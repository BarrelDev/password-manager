import os
import io
import pandas as pd
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

DATA_FOLDER = ".dat/"
FIELD_NAMES = ["service", "usrname", "passwd"]

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
    if os.path.exists(DATA_FOLDER+"salt"):
        with open(DATA_FOLDER+"salt", "rb") as file:
            salt = file.read()
            return salt
    else:
        salt = os.urandom(16)
        write_binary_data(salt, "salt")
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

def get_dataframe(password):
    f = Fernet(get_key(password))

    read_dat = f.decrypt(read_binary_data("data")).decode('utf-8')
    input = io.StringIO(read_dat)
    df_read = pd.read_csv(input)

    return df_read

def write_dataframe(password, df):
    f = Fernet(get_key(password))

    # Save to CSV in-memory using pandas
    output = io.StringIO()
    df.to_csv(output, index=False)
    csv_data = output.getvalue()
    print(csv_data)

    # Encrypt and save to file
    token = f.encrypt(csv_data.encode('utf-8'))
    write_binary_data(token, "data")

def add_service(password, service: str, usrname: str, passwd: str):
    df = get_dataframe(password)
   
    #Remove old credentials if service already exists.
    df = df[df["service"] != service]

    row = [service, usrname, passwd]
    df = pd.concat([df, pd.DataFrame([row],
                                     columns=FIELD_NAMES)],
                   ignore_index=True)
    
    write_dataframe(password, df)

def remove_service(password, service: str):
    df = get_dataframe(password)

    df = df[df["service"] != service]

    write_dataframe(password, df)

def get_credentials(password, service: str):
    df = get_dataframe(password)
    row = df.loc[df["service"] == service]
    if not row.empty:
        return row.iloc[0]["usrname"], row.iloc[0]["passwd"]
    return None, None

def get_services(password):
    df = get_dataframe(password)

    return df["service"].unique().tolist()
