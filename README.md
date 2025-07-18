# password-manager
A simple, local-first, password manager written in python. Offers both CLI and TUI uses. Licensed under GNU GPL v3

# Run from source
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

# Command-Line Interface (CLI) Usage

### Help

`python main.py help` or `python main.py --help` will show print the different arguments and commands

### Setup

For first-time users, run `python main.py setup` to begin the setup process. This will create a database and secure it with a password.

### List

List out the stored services in the database. Prompts for master password.

```
python main.py list
```

### Add

Adds/overrides a service stored in the database. Prompts for master password and service password.

```
python main.py add [SERVICE] [USERNAME]
```

### Remove

Removes a service stored in the database. Prompts for master password.

```
python main.py remove [SERVICE]
```

### Get

Retrives credentials for a service. Prompts for master password.

```
python main.py get [SERVICE]
```

### Search

Does a fuzzy search based on a query. Prompts for master password.

```
python main.py search [QUERY]
```

### Lock

Deletes session file and locks database. Does not prompt for master password.

```
python main.py lock
```

# Terminal UI (TUI) Usage

To use the password manager as a TUI, simply run
```
python main.py
```
For first-time users, a setup menu will appear and will prompt for a master password. 

All features are available from the main menu.