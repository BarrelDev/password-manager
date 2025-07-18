from screens.mainmenu import MainMenu
from data import data_exists, get_fernet, get_key, add_service, remove_service, get_credentials, is_valid, save_session_key

from textual.app import App, ComposeResult
from textual.widgets import Input, Label, Button, Static
from textual.containers import Vertical
from textual.reactive import reactive

class LoginApp(App):
    CSS_PATH = "styles.css"

    password = reactive("")
    message = reactive("")
    session_exists = reactive(False)

    def compose(self) -> ComposeResult:
        if not self.session_exists:
            yield Vertical(
                Label("🔐 Welcome to Password Manager", id="title"),
                Input(password=True, placeholder="Password", id="password"),
                Button("Login", id="login_button"),
                Static(id="msg")
            )
        else:
            yield MainMenu()    

    def on_mount(self) -> None:
        if not data_exists():
            self.message = "❌ No data found. Please run `setup` to initialize the password manager."
        else:
            try:
                self.fernet = get_fernet()
                self.session_exists = True  # Save the session key
                self.push_screen(MainMenu())
            except ValueError:
                self.session_exists = False
    
    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "password":
            self.password = event.value

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "password":
            self.submit_password()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login_button":
            self.submit_password()

    def submit_password(self):
        if self.password:
            password = self.password.encode('utf-8')
            if not data_exists():
                self.message = "❌ No data found. Please run `setup` to initialize the password manager."
            if (is_valid(get_fernet(password))):
                self.fernet = get_fernet(password)
                save_session_key(get_key(password))
                self.session_exists = True
                self.password = ""
                self.push_screen(MainMenu())
            else:
                self.message = "❌ Invalid password. Please try again."
        else:
            self.message = "❌ Please enter a password."
        self.query_one("#msg", Static).update(self.message)
        self.query_one("#password", Input).value = ""

if __name__ == "__main__":
    app = LoginApp()
    app.run()
