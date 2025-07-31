####################
## CONFIG METHODS ##
####################

import json
import sys
from pathlib import Path
from platformdirs import user_config_dir

APP_NAME = "PasswordManager"

CONFIG_DIR = Path(user_config_dir(APP_NAME))
CONFIG_PATH = CONFIG_DIR / "config.json"

def get_builtin_styles_path() -> Path:
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller bundled path
        return Path(sys._MEIPASS) / "styles.css"
    else:
        # Regular dev path
        return Path(__file__).parent.parent / "tui" / "styles.css"

CUSTOM_STYLES_PATH = CONFIG_DIR / "styles.css"
BUILTIN_STYLES_PATH = get_builtin_styles_path()

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

def get_data_folder() -> Path:
    config = load_config()
    folder = config.get("storage_dir", DEFAULT_DATA_FOLDER)
    full_path = (CONFIG_DIR / folder).resolve()
    full_path.mkdir(parents=True, exist_ok=True)
    return full_path

def get_styles_paths() -> list[Path]:
    paths = [BUILTIN_STYLES_PATH]
    if CUSTOM_STYLES_PATH.exists():
        paths.append(CUSTOM_STYLES_PATH)
    return paths