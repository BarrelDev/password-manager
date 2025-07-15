import os

DATA_FOLDER = ".dat/"

def write_binary_data(data, filename):
    if os.path.isdir(DATA_FOLDER):
        with open(DATA_FOLDER + filename, 'xb+') as file:
            file.write(data)
    else:
        os.mkdir(DATA_FOLDER)
        with open(DATA_FOLDER + filename, 'xb+') as file:
            file.write(data)

def get_salt():
    if os.path.exists(DATA_FOLDER+"salt"):
        with open(DATA_FOLDER+"salt", "rb") as file:
            return file.read()
    else:
        salt = os.urandom(16)
        write_binary_data(salt, "salt")
        return salt
            
