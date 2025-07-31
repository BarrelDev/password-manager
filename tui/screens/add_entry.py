from textual.screen import Screen
from textual.widgets import Button, Label, DataTable, Static, Input, Checkbox
from textual.containers import Vertical, Horizontal
import string
import secrets

from core.data import get_dataframe, add_service

class AddEntry(Screen):
    def compose(self):
        self.generated_password = ""
        self.df = get_dataframe(self.app.fernet)

        # Input fields row
        input_row = Horizontal(
            Input(placeholder="Service", id="service-input").focus(),
            Input(placeholder="Username", id="username-input"),
            Input(placeholder="Password", password=True, id="password-input"),
            Button("Add Entry", id="add"),
            id="input-fields"
        )

        # Control buttons
        button_row = Horizontal(
            Label("➕ Add Entry", id="title"),
            Button("Back to Main Menu", id="back"),
            id="buttons"
        )

        yield Vertical(
            button_row,
            input_row,
            Horizontal(
                Input(value="16", id="pw-length", placeholder="Length"),
                Checkbox("Uppercase", id="upper", value=True),
                Checkbox("Lowercase", id="lower", value=True),
                Checkbox("Digits", id="digits", value=True),
                Checkbox("Symbols", id="symbols", value=True),
                Button("Generate", id="generate"),
                id="gen-controls"
            ),
            Input(placeholder="Generated password", id="gen-display", disabled=True),
            Static("", id="message"),
            id="main-layout"
        )

    def on_mount(self):
        self.query_one("#service-input", Input).focus()

    def on_screen_resume(self):
        self.query_one("#service-input", Input).focus()
    
    def on_key(self, event):
        if event.key == "escape" or event.key == "q":
            self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "add":
                service = self.query_one("#service-input", Input).value.strip()
                username = self.query_one("#username-input", Input).value.strip()
                password = self.query_one("#password-input", Input).value.strip()
                if not service or not username or not password:
                    self.query_one("#message", Static).update("⚠️ Fill all fields.")
                    return

                # Add to DataFrame and table
                add_service(self.app.fernet, service, username, password)
                self.df = get_dataframe(self.app.fernet)  # Reload DataFrame

                # Clear inputs and Notify
                for field_id in ["#service-input", "#username-input", "#password-input"]:
                    self.query_one(field_id, Input).value = ""
                self.query_one("#message", Static).update("✅ Entry added.")
                self.query_one("#service-input", Input).focus()
            case "back":
                self.app.pop_screen()
            case "generate":
                self._generate_password()

    def _generate_password(self):
        length_input = self.query_one("#pw-length", Input).value
        try:
            length = int(length_input)
        except ValueError:
            self.query_one("#message", Static).update("❌ Invalid length.")
            return

        use_upper = self.query_one("#upper", Checkbox).value
        use_lower = self.query_one("#lower", Checkbox).value
        use_digits = self.query_one("#digits", Checkbox).value
        use_symbols = self.query_one("#symbols", Checkbox).value

        charsets = ""
        if use_upper:
            charsets += string.ascii_uppercase
        if use_lower:
            charsets += string.ascii_lowercase
        if use_digits:
            charsets += string.digits
        if use_symbols:
            charsets += string.punctuation

        if not charsets:
            self.query_one("#message", Static).update("❌ No character sets selected.")
            return

        self.generated_pw = ''.join(secrets.choice(charsets) for _ in range(length))
        self.query_one("#gen-display", Input).value = self.generated_pw
        self.query_one("#password-input", Input).value = self.generated_pw
