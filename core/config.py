####################
## CONFIG METHODS ##
####################

import json
from pathlib import Path
from platformdirs import user_config_dir

APP_NAME = "PasswordManager"

CONFIG_DIR = Path(user_config_dir(APP_NAME))
CONFIG_PATH = CONFIG_DIR / "config.json"

DEFAULT_DATA_FOLDER = ".dat/"

DEFAULT_CONFIG = {
    "storage_dir": DEFAULT_DATA_FOLDER,  # Default storage location inside config dir
}

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def get_data_folder() -> str:
    DATA_FOLDER = load_config()["storage_dir"] + "/"
    DATA_FOLDER = DATA_FOLDER.replace("\\", "/")  # Ensure forward slashes for compatibility
    return DATA_FOLDER
