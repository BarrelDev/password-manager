import data
import io
from cryptography.fernet import Fernet
import pandas as pd

PASSWORD = b"password"
FIELD_NAMES = ["service", "usrname", "passwd"]

f = Fernet(data.get_key(PASSWORD))

df = pd.DataFrame(columns=FIELD_NAMES)
df = pd.concat([df, pd.DataFrame([["google", "name", "password"]], columns=FIELD_NAMES)], ignore_index=True)

# Save to CSV in-memory using pandas
output = io.StringIO()
df.to_csv(output, index=False)
csv_data = output.getvalue()
print(csv_data)

# Encrypt and save to file
token = f.encrypt(csv_data.encode('utf-8'))
data.write_binary_data(token, "data")

# Read and decrypt data from file
read_dat = f.decrypt(data.read_binary_data("data")).decode('utf-8')
print(read_dat)

# Load back into DataFrame using pandas
input = io.StringIO(read_dat)
df_read = pd.read_csv(input)

# Print the dataframe
print(df_read)
