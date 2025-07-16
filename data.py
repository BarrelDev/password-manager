import os
import io
import csv

DATA_FOLDER = ".dat/"
FIELD_NAMES = ["service", "usrname", "passwd"]

def write_binary_data(data, filename: str):
    if os.path.isdir(DATA_FOLDER):
        with open(DATA_FOLDER + filename, 'wb+') as file:
            file.write(data)
            file.close()
    else:
        os.mkdir(DATA_FOLDER)
        with open(DATA_FOLDER + filename, 'wb+') as file:
            file.write(data)
            file.close()

def read_binary_data(filename: str):
    try:
        with open(DATA_FOLDER + filename, 'rb') as file:
            dat = file.read()
            return dat
    except:
        print ('No such file %s exists' % filename)
        return b''

def get_salt():
    if os.path.exists(DATA_FOLDER+"salt"):
        with open(DATA_FOLDER+"salt", "rb") as file:
            salt = file.read()
            file.close()
            return salt
    else:
        salt = os.urandom(16)
        write_binary_data(salt, "salt")
        return salt

