from textual.screen import Screen
from textual.widgets import Button, Label, DataTable, Static, Input, Checkbox
from textual.containers import Vertical, Horizontal
import string
import secrets

from core.data import get_dataframe, add_service

class AddEntry(Screen):
    def on_key(self, event):
        if event.key == "escape" or event.key == "q":
            self.app.pop_screen()
    
    def on_mount(self):
        self.query_one("#service-input", Input).focus()

    def on_screen_resume(self):
        self.query_one("#service-input", Input).focus()

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

        # Populate the table
        self.table = DataTable(id="entry-table")
        self.table.cursor_type = "row"
        _, _, self.password_key = self.table.add_columns("Service", "Username", "Password")
        masked = "••••••"
        self.real_passwords = {}  # Store real passwords for later use
        for _, row in self.df.iterrows():
            key = self.table.add_row(row["service"], row["usrname"], masked)
            self.real_passwords[key] = row["passwd"]

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
    
    def generate_password(self):
        length_input = self.query_one("#pw-length", Input).value
        try:
            length = int(length_input)
        except ValueError:
            self.query_one("#msg", Static).update("❌ Invalid length.")
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
            self.query_one("#msg", Static).update("❌ No character sets selected.")
            return

        self.generated_pw = ''.join(secrets.choice(charsets) for _ in range(length))
        self.query_one("#gen-display", Input).value = self.generated_pw
        self.query_one("#password-input", Input).value = self.generated_pw

    def on_data_table_row_highlighted(self, event) -> None:
        # Mask all passwords
        for row_key in self.real_passwords:
            self.table.update_cell(row_key, self.password_key, "••••••")

        # Reveal the highlighted password
        highlighted_key = event.row_key
        real_password = self.real_passwords.get(highlighted_key)
        if real_password is not None:
            self.table.update_cell(highlighted_key, self.password_key, real_password)

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
                self.generate_password()
