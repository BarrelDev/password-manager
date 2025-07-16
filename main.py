import data
import csv
import io
from cryptography.fernet import Fernet

PASSWORD = b"password"
FIELD_NAMES = ["service", "usrname", "passwd"]

f = Fernet(data.get_key(PASSWORD))

output = io.StringIO()
writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
writer.writerow(FIELD_NAMES)
writer.writerow(["google", "name", "password"])
print(output.getvalue())
table = output.getvalue()
token = f.encrypt(table.encode('ascii'))

data.write_binary_data(token, "data")

read_dat = f.decrypt(data.read_binary_data("data")).decode('ascii')

print(read_dat)


