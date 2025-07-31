# password-manager
A simple, local-first password manager written in Python.  
Provides both a **Terminal UI (TUI)** and **Command-Line Interface (CLI)** with secure encryption, Vim-style navigation, and modern UI design.

Licensed under GNU GPL v3.


## Features

- 🔐 AES-encrypted password storage (Fernet)
- 🧠 Session caching (like `sudo`) with auto-lock on quit
- 🖥️ TUI built with [Textual](https://github.com/Textualize/textual)
- 🔍 Fuzzy search and clipboard copy
- 🧪 Full CLI interface for scripting
- 🧩 Vim-style navigation: `j/k`, `g/G`, `/`, `dd`, `r`
- 🎨 Theme extensibility with custom `styles.css`

## Table of Contents
1. [Terminal UI (TUI) Usage](#terminal-ui-tui-usage)
2. [Command Line Interface (CLI) Usage](#command-line-interface-cli-usage)
3. [Configuration](#config-file)
    1. [Format](#format)
    2. [Custom CSS](#custom-css)
4. [Run/Build from source](#runbuild-from-source)
    1. [Setup virtual environment](#setup-the-virtual-environment)
    2. [Run](#run)
    3. [Build](#build)

## Terminal UI (TUI) Usage

This is the intended way to use the password manager

To use the password manager as a TUI, simply run
```
password-manager
```
For first-time users, a setup menu will appear and will prompt for a master password. 

All features are available from the main menu.

Users can use Tab or a Mouse to navigate menus.

Supports Vim-style bindings for navigating the entries table.

### Bindings

| Keys | Action |
|------|--------|
| `j`,`k` | for going up/down menus |
`g` | to go to first entry in the table
`G`| to go to last entry in the table
`a`,`i` | to add an entry
`dd`| to delete an entry
`r` | to replace the username/password for an entry
`/` | to open fuzzy search menu
`Esc`, `q` | to exit menus, locks session from main menu
`Ctrl + q` | closes the application


## Command-Line Interface (CLI) Usage

#### Help

`password-manager help` or `password-manager --help` will list the different arguments and commands

#### Setup

For first-time users, run `password-manager setup` to begin the setup process. This will create a database and secure it with a password.

#### List

List out the stored services in the database. Prompts for master password.

```
password-manager list
```

#### Add

Adds/overrides a service stored in the database. Prompts for master password and service password.

```
password-manager add [SERVICE] [USERNAME]
```

#### Remove

Removes a service stored in the database. Prompts for master password.

```
password-manager remove [SERVICE]
```

#### Get

Retrives credentials for a service. Prompts for master password.

```
password-manager get [SERVICE]
```

#### Search

Does a fuzzy search based on a query. Prompts for master password.

```
password-manager search [QUERY]
```

#### Lock

Deletes session file and locks database. Does not prompt for master password.

```
password-manager lock
```

#### Config

`--set-dir` sets the path of the data file used to store passwords

```
password-manager config --set-dir [DATA_FILE_PATH]
```

## Configuration

A `config.json` file is stored in `%APPDATA%/PasswordManager` on Windows systems and in `~\.config\PasswordManager`on Unix-based systems

### Format

```
{
    "storage_dir": [DATA_FILE_PATH]
}
```

### Custom CSS

You can add custom CSS for the app by adding a `styles.css` file into the config folder. 

Your styles will be applied **after** the built-in styles, allowing you to override only what you want.

#### Example

```css
Screen {
  background: black;
}

Button {
  background: #3a3a3a;
  color: white;
}
```

## Run/Build from source
Run the following commands from the root directory of the repository to run the code from source.

### Setup the virtual environment

#### Windows

```pwsh
python -m venv .venv
.venv\scripts\activate
pip install -r requirements.txt
```

#### Unix-based (Linux/MacOS/etc.)

```bash
python -m venv .venv
# [FILETYPE] may be .sh, .fish, etc. depending on your shell.
source .venv/scripts/activate.[FILETYPE]
pip install -r requirements.txt
```

### Run
```
python main.py
```

### Build
```
pyinstaller password-manager.spec
```

This will create an executable file for your respective operating system in the `dist` folder

## Security Notes

- Passwords are encrypted with a master key derived using PBKDF2 + SHA256 + Salt.
- Session key is cached securely using OS-based credential storage and auto-expires after inactivity.
    - On Windows, "Windows Credential Locker"
    - On MacOS, "Keychain"
    - On Linux, "Secret Service"

As such, Linux users may need to install `secretstorage` using
```
pip install secretstorage
```

KDE4 / KDE 5 users can alternatively take advantage of **KWallet** by instead installing `dbus-python`.