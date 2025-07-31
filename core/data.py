#######################
## DATAFRAME METHODS ##
#######################

import io
import pandas as pd

from core.crypto import get_data_file, write_data_file

FIELD_NAMES = ["service", "usrname", "passwd"]

def get_dataframe(f):
    read_dat = get_data_file(f)

    if read_dat is None:
        return create_empty_dataframe()

    input = io.StringIO(read_dat)
    df_read = pd.read_csv(input)
    return df_read  

def write_dataframe(f, df):
    # Save to CSV in-memory using pandas
    output = io.StringIO()
    df.to_csv(output, index=False)
    csv_data = output.getvalue()

    # Encrypt and save to file
    write_data_file(f, csv_data)

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
