import base64
import os
import data
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

PASSWORD = b"password"

salt = data.get_salt()

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=1_200_000,
)

key = base64.urlsafe_b64encode(kdf.derive(PASSWORD))
f = Fernet(key)

data = b"secret message"
token = f.encrypt(data)
print (token)


