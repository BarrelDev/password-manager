import os
import io
import pandas as pd
from cryptography.fernet import InvalidToken

from core.config import get_data_folder
from core.crypto import get_salt

DATA_FILE = "data"
SALT_SIZE = 16
FIELD_NAMES = ["service", "usrname", "passwd"]


########################
## READ/WRITE METHODS ##
########################

def write_binary_data(data, filename: str):
    path = os.path.join(get_data_folder(), filename)
    os.makedirs(get_data_folder(), exist_ok=True)
    with open(path, 'wb+') as file:
        file.write(data)

def read_binary_data(filename: str):
    try:
        path = os.path.join(get_data_folder(), filename)
        with open(path, 'rb') as file:
            dat = file.read()
            return dat
    except FileNotFoundError:
        print ('No such file %s exists' % filename)
        return None

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
    except FileNotFoundError:
        print(f"No such file {DATA_FILE} exists")
        return create_empty_dataframe()

    return create_empty_dataframe()      

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
