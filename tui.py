from screens.mainmenu import EntryList
from data import data_exists, get_fernet, get_key, is_valid, save_session_key, write_dataframe, create_empty_dataframe

from textual.app import App, ComposeResult
from textual.widgets import Input, Label, Button, Static, Checkbox
from textual.containers import Vertical
from textual.reactive import reactive

class LoginApp(App):
    CSS_PATH = "styles.css"

    password = reactive("")
    confirm_password = reactive("")
    message = reactive("")
    session_exists = reactive(False)

    def compose(self) -> ComposeResult:
        if not data_exists():
            yield Vertical(
                Label("🔐 Welcome to Password Manager!", id="title"),
                Static("Please create a master password.", id="msg"),
                Input(password=True, placeholder="Password", id="password"),
                Input(password=True, placeholder="Confirm Password", id="confirm_password"),
                Checkbox("Remember me", id="remember_me", value=True),
                Button("Create", id="create_button")
            )
        elif not self.session_exists:
            yield Vertical(
                Label("🔐 Welcome to Password Manager", id="title"),
                Input(password=True, placeholder="Password", id="password"),
                Checkbox("Remember me", id="remember_me", value=True),
                Button("Login", id="login_button"),
                Static(id="msg")
            )
        else:
            yield EntryList()    

    def on_mount(self) -> None:
        if not data_exists():
            self.message = "❌ No data found. Please run `setup` to initialize the password manager."
        else:
            try:
                self.fernet = get_fernet()
                self.session_exists = True  # Save the session key
                self.push_screen(EntryList())
            except ValueError:
                self.session_exists = False
    
    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "password":
            self.password = event.value
        if event.input.id == "confirm_password":
            self.confirm_password = event.value

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "password" and data_exists():
            self.submit_password()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login_button":
            self.submit_password()
        if event.button.id == "create_button":
            self.setup_password()

    def submit_password(self):
        if self.password:
            password = self.password.encode('utf-8')
            if not data_exists():
                self.message = "❌ No data found. Please run `setup` to initialize the password manager."
            if (is_valid(get_fernet(password))):
                self.fernet = get_fernet(password)
                self.password = ""
                if (remember_me := self.query_one("#remember_me", Checkbox)).value:
                    save_session_key(get_key(password))
                    self.session_exists = True
                self.push_screen(EntryList())
            else:
                self.message = "❌ Invalid password. Please try again."
        else:
            self.message = "❌ Please enter a password."
        self.query_one("#msg", Static).update(self.message)
        self.query_one("#password", Input).value = ""

    def setup_password(self):
        if self.password and self.confirm_password:
            if self.password == self.confirm_password:
                if len(self.password) < 8:
                    self.message = "❗ Password must be at least 8 characters."
                else:
                    password = self.password.encode('utf-8')
                    save_session_key(get_key(password))
                    self.fernet = get_fernet(password)
                    write_dataframe(self.fernet, create_empty_dataframe())  # Initialize empty DataFrame
                    self.session_exists = True
                    self.push_screen(EntryList())
            else:
                self.message = "❗ Passwords do not match."
        else:
            self.message = "❌ Please enter both password fields."
        self.query_one("#msg", Static).update(self.message)


if __name__ == "__main__":
    app = LoginApp()
    app.run()
