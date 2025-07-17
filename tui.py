from screens.mainmenu import MainMenu
from data import data_exists, get_fernet, add_service, remove_service, get_credentials

from textual.app import App, ComposeResult
from textual.widgets import Input, Label, Button, Static
from textual.containers import Vertical
from textual.reactive import reactive

class LoginApp(App):
    CSS_PATH = "styles.css"

    password = reactive("")
    message = reactive("")

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("🔐 Welcome to Password Manager", id="title"),
            Input(password=True, placeholder="Password", id="password"),
            Button("Login", id="login_button"),
            Static(id="msg")
        )

    def on_mount(self) -> None:
        if not data_exists():
            self.message = "❌ No data found. Please run `setup` to initialize the password manager."
        else:
            try:
                self.fernet = get_fernet()
                self.push_screen(MainMenu())
            except ValueError:
                pass

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "password":
            self.password = event.value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login_button":
            if self.password:
                self.message = f"✅ Welcome!"
            else:
                self.message = "❌ Please enter a password."
            self.query_one("#msg", Static).update(self.message)

if __name__ == "__main__":
    app = LoginApp()
    app.run()
