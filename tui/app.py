from tui.screens import EntryList, Search, AddEntry

from core.config import load_config, save_config, DEFAULT_DATA_FOLDER, get_styles_paths
from core.crypto import get_fernet, get_key, is_valid, data_exists
from core.session import save_session_key
from core.data import write_dataframe, create_empty_dataframe

from textual.app import App, ComposeResult
from textual.widgets import Input, Label, Button, Static, Checkbox
from textual.containers import Vertical
from textual.reactive import reactive

class LoginApp(App):
    CSS_PATH = get_styles_paths()

    # Widget IDs
    TITLE_ID = "title"
    PASSWORD_ID = "password"
    CONFIRM_PASSWORD_ID = "confirm_password"
    DATA_PATH_ID = "data_file_path"
    MESSAGE_ID = "msg"
    LOGIN_BUTTON_ID = "login_button"
    CREATE_BUTTON_ID = "create_button"
    REMEMBER_ME_ID = "remember_me"

    MAIN_SCREEN_ID = "main"

    password = reactive("")
    confirm_password = reactive("")
    message = reactive("")
    session_exists = reactive(False)

    def compose(self) -> ComposeResult:
        if not data_exists():
            yield self._compose_setup()
        elif not self.session_exists:
            yield self._compose_login()
        else:
            self.push_screen(self.MAIN_SCREEN_ID)

    def on_mount(self) -> None:
        self._install_screens()
        self._init_session()
    
    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == self.PASSWORD_ID:
            self.password = event.value
        if event.input.id == self.CONFIRM_PASSWORD_ID:
            self.confirm_password = event.value

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == self.PASSWORD_ID and data_exists():
            self._submit_password()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == self.LOGIN_BUTTON_ID:
            self._submit_password()
        if event.button.id == self.CREATE_BUTTON_ID:
            self._setup_password()

    def _submit_password(self):
        if self.password:
            password = self.password.encode('utf-8')
            if not data_exists():
                self.message = "❌ No data found. Please run `setup` to initialize the password manager."
            if (is_valid(get_fernet(password))):
                self.fernet = get_fernet(password)
                self.password = ""
                if (self.query_one(f"#{self.REMEMBER_ME_ID}", Checkbox)).value:
                    save_session_key(get_key(password))
                    self.session_exists = True
                self.push_screen(self.MAIN_SCREEN_ID)
            else:
                self.message = "❌ Invalid password. Please try again."
        else:
            self.message = "❌ Please enter a password."
        self.query_one(f"#{self.MESSAGE_ID}", Static).update(self.message)
        self.query_one(f"#{self.PASSWORD_ID}", Input).value = ""

    def _setup_password(self):
        if self.password and self.confirm_password:
            if self.password == self.confirm_password:
                if len(self.password) < 8:
                    self.message = "❗ Password must be at least 8 characters."
                else:
                    config = load_config()
                    config["storage_dir"] = self.query_one(f"#{self.DATA_PATH_ID}", Input).value
                    save_config(config)
                    password = self.password.encode('utf-8')
                    save_session_key(get_key(password))
                    self.fernet = get_fernet(password)
                    write_dataframe(self.fernet, create_empty_dataframe())  # Initialize empty DataFrame
                    self.session_exists = True
                    self.push_screen(self.MAIN_SCREEN_ID)
            else:
                self.message = "❗ Passwords do not match."
        else:
            self.message = "❌ Please enter both password fields."
        self.query_one(f"#{self.MESSAGE_ID}", Static).update(self.message)

    def _compose_setup(self) -> Vertical:
        # Setup screen for first-time users
        return Vertical(
            Label("🔐 Welcome to Password Manager!", id=self.TITLE_ID),
            Static("Please create a master password.", id=self.MESSAGE_ID),
            Input(password=True, placeholder="Password", id=self.PASSWORD_ID),
            Input(password=True, placeholder="Confirm Password", id=self.CONFIRM_PASSWORD_ID),
            Static("Data File Path", id="msg_path"),
            Input(value=DEFAULT_DATA_FOLDER, placeholder="Data File Path", id=self.DATA_PATH_ID),
            Checkbox("Remember me", id=self.REMEMBER_ME_ID, value=True),
            Button("Create", id=self.CREATE_BUTTON_ID)
        )

    def _compose_login(self) -> Vertical:
        return Vertical(
            Label("🔐 Welcome to Password Manager", id=self.TITLE_ID),
            Input(password=True, placeholder="Password", id=self.PASSWORD_ID),
            Checkbox("Remember me", id=self.REMEMBER_ME_ID, value=True),
            Button("Login", id=self.LOGIN_BUTTON_ID),
            Static(id=self.MESSAGE_ID)
        )

    def _install_screens(self):
        self.install_screen(EntryList(), name=self.MAIN_SCREEN_ID)
        self.install_screen(AddEntry(), name="add")
        self.install_screen(Search(), name="search")

    def _init_session(self):
        if not data_exists():
            self.message = "❌ No data found. Please run `setup` to initialize the password manager."
        else:
            try:
                self.fernet = get_fernet()
                self.session_exists = True  # Save the session key
                self.push_screen(self.MAIN_SCREEN_ID)
            except ValueError:
                self.session_exists = False
        
if __name__ == "__main__":
    app = LoginApp()
    app.debug()
