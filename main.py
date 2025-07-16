import base64
import data
import csv
import io
import uuid
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

PASSWORD = b"password"
FIELD_NAMES = ["service", "usrname", "passwd"]

salt = data.get_salt()

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=1_200_000,
)

key = base64.urlsafe_b64encode(kdf.derive(PASSWORD))
f = Fernet(key)

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


