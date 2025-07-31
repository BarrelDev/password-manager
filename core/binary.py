########################
## READ/WRITE METHODS ##
########################

import os
from core.config import get_data_folder

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
