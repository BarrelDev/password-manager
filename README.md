# password-manager
A simple, local-first, password manager written in python. Offers both CLI and TUI uses. Supports Vim-style bindings in TUI mode. Licensed under GNU GPL v3

# Table of Contents
1. [Run/Build from source](#runbuild-from-source)
    1. [Setup virtual environment](#setup-the-virtual-environment)
    2. [Run](#run)
    3. [Build](#build)
2. [Terminal UI (TUI) Usage](#terminal-ui-tui-usage)
3. [Command Line Interface (CLI) Usage](#command-line-interface-cli-usage)
4. [Config File](#config-file)
    1. [Format](#format)

# Run/Build from source
Run the following commands from the root directory of the repository to run the code from source.

## Setup the virtual environment

### Windows

```
python -m venv .venv
.venv\scripts\activate
pip install -r requirements.txt
```

### Unix-based (Linux/MacOS/etc.)

```
python -m venv .venv
# [FILETYPE] may be .sh, .fish, etc. depending on your shell.
source .venv/scripts/activate.[FILETYPE]
pip install -r requirements.txt
```

## Run
```
python main.py
```

## Build
```
pyinstaller password-manager.spec
```

This will create an executable file for your respective operating system in the `dist` folder

# Terminal UI (TUI) Usage

This is the intended way to use the password manager

To use the password manager as a TUI, simply run
```
password-manager
```
For first-time users, a setup menu will appear and will prompt for a master password. 

All features are available from the main menu.

Users can use Tab or a Mouse to navigate menus.

Supports Vim-style bindings for navigating the entries table.

## Bindings

`j`,`k` for going up/down menus

`g` to go to first entry in the table

`G` to go to last entry in the table

`a`,`i` to add an entry

`dd` to delete an entry

`r` to replace the username/password for an entry

`/` to open fuzzy search menu

`Esc`, `q` to exit menus

- Locks session from main menu

`Ctrl + q` closes the application


# Command-Line Interface (CLI) Usage

### Help

`password-manager help` or `password-manager --help` will show print the different arguments and commands

### Setup

For first-time users, run `password-manager setup` to begin the setup process. This will create a database and secure it with a password.

### List

List out the stored services in the database. Prompts for master password.

```
password-manager list
```

### Add

Adds/overrides a service stored in the database. Prompts for master password and service password.

```
password-manager add [SERVICE] [USERNAME]
```

### Remove

Removes a service stored in the database. Prompts for master password.

```
password-manager remove [SERVICE]
```

### Get

Retrives credentials for a service. Prompts for master password.

```
password-manager get [SERVICE]
```

### Search

Does a fuzzy search based on a query. Prompts for master password.

```
password-manager search [QUERY]
```

### Lock

Deletes session file and locks database. Does not prompt for master password.

```
password-manager lock
```

### Config

`--set-dir` sets the path of the data file used to store passwords

```
password-manager config --set-dir [DATA_FILE_PATH]
```

# Config File

A `config.json` file is stored in `%APPDATA%/PasswordManager` on Windows systems and in `~\.config\PasswordManager`on Unix-based systems

## Format

```
{
    "storage_dir": [DATA_FILE_PATH
}
```