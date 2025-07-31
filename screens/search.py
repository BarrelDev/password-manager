from textual.screen import Screen
from textual.widgets import Button, Label, DataTable, Input
from textual.containers import Vertical, Horizontal

from rapidfuzz import process
import pyperclip

from data import get_services, get_credentials

class Search(Screen):
    def on_key(self, event):
        key = event.key
        if key == "escape" or key == "q":
            self.app.pop_screen()

        if key == "j":
            self.table.action_cursor_down()
        elif key == "k":
            self.table.action_cursor_up()
        elif key == "g":  # Go to top
            self.table.cursor_coordinate = (0, 0)
        elif key == "G":  # Go to bottom
            if self.table.row_count > 0:
                self.table.cursor_coordinate = (self.table.row_count - 1, 0)
        elif event.key == "enter":
            self.copy_selected_password()

    def copy_selected_password(self):
        if self.table.cursor_row is not None and self.table.has_focus:
            index = self.table.cursor_row
            row_key, _ = self.table.coordinate_to_cell_key(self.table.cursor_coordinate)
            password = self.real_passwords.get(row_key)

            if password:
                try:
                    pyperclip.copy(password)
                    self.app.set_focus(self.table)
                    self.app.bell()  # Optional: feedback
                    self.app.notify("📋 Password copied to clipboard.")
                except Exception as e:
                    self.app.notify(f"❌ Copy failed: {str(e)}", severity="error")

    def compose(self):
        self.real_passwords = {}  # Store real passwords for later use
        self.table = DataTable(id="search-results")
        _, _, self.password_key = self.table.add_columns("Service", "Username", "Password")
        self.table.cursor_type = "row"

        yield Vertical(
            Horizontal(
                Label("🔍 Search Entries", id="title"),
                Button("Back to Main Menu", id="back"),
                id="header"),
            Horizontal(
                Input(placeholder="Search by service name", id="search-input").focus(),
                id="search-controls"
            ),
            self.table,
            id="main-layout"
        )

    def on_button_pressed(self, event):
        if event.button.id == "back":
            self.app.pop_screen()  # go back to main menu

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search-input":
            self.submit_search()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input":
            self.submit_search()

    def submit_search(self):
        # Logic to perform search and display results
        query = self.query_one("#search-input", Input).value.strip()
        if not query:
            self.query_one("#search-results", DataTable).clear()
            self.real_passwords.clear()
            return

        # Perform search
        services = get_services(self.app.fernet)
        results = process.extract(query, services, limit=5, score_cutoff=60)
        results.sort(key=lambda x: x[1], reverse=True)

        # Update the search results table
        self.query_one("#search-results", DataTable).clear()
        self.real_passwords.clear()
        for service, _, _ in results:
            username, password = get_credentials(self.app.fernet, service)
            key = self.query_one("#search-results", DataTable).add_row(service, username, password)
            self.real_passwords[key] = password

    def on_data_table_row_highlighted(self, event) -> None:
        # Mask all passwords
        for row_key in self.real_passwords:
            self.table.update_cell(row_key, self.password_key, "••••••")

        # Reveal the highlighted password
        highlighted_key = event.row_key
        real_password = self.real_passwords.get(highlighted_key)
        if real_password is not None:
            self.table.update_cell(highlighted_key, self.password_key, real_password)