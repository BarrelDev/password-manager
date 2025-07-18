from textual.screen import Screen
from textual.widgets import Button, Label, DataTable
from textual.containers import Vertical, Horizontal

from data import lock_session, get_dataframe

class MainMenu(Screen):
    def compose(self):
        yield Vertical(
            Label("📂 Main Menu", id="title"),
            Button("📋 View All Entries", id="view"),
            Button("➕ Add Entry", id="add"),
            Button("🔍 Search", id="search"),
            Button("🔒 Lock", id="lock"),
        )

    def on_button_pressed(self, event):
        if event.button.id == "view":
            self.app.push_screen(EntryList())
        elif event.button.id == "add":
            self.app.push_screen(AddEntry())
        elif event.button.id == "search":
            self.app.push_screen(Search())
        elif event.button.id == "lock":
            lock_session()
            self.app.pop_screen()  # go back to login


class EntryList(Screen):
    def compose(self):
        df = get_dataframe(self.app.fernet)

        header = Horizontal(
            Label("🔍 Entry List", id="title"),
            Button("Back to Main Menu", id="back"),
            id="header"
        )

        # This would be populated with actual entries
        if not df.empty:
            table = DataTable(id="table")
            table.add_columns("Service", "Username", "Password")
            for _, row in df.iterrows():
                table.add_row(row["service"], row["usrname"], row["passwd"])
            table.focus()
            yield Vertical(
                header,
                table,
                id="list-container"
            )
        else:
            yield Vertical(
                header,
                Label("No entries available yet.", id="entries"),
                id="list-container"
            )

    def on_button_pressed(self, event):
        if event.button.id == "back":
            self.app.pop_screen()  # go back to main menu

    def on_mount(self):
        # Load entries from data source and display them
        pass  # Implement loading logic here

class AddEntry(Screen):
    def compose(self):
        yield Label("➕ Add New Entry", id="title")
        yield Button("Back to Main Menu", id="back")
        # Add input fields for service, username, and password
        yield Button("Save", id="save")

    def on_button_pressed(self, event):
        if event.button.id == "back":
            self.app.pop_screen()  # go back to main menu
        if event.button.id == "save":
            # Logic to save the new entry
            self.app.pop_screen()  # go back to main menu

class Search(Screen):
    def compose(self):
        yield Label("🔍 Search Entries", id="title")
        yield Button("Back to Main Menu", id="back")
        # Add input field for search term
        yield Button("Search", id="search")

    def on_button_pressed(self, event):
        if event.button.id == "back":
            self.app.pop_screen()  # go back to main menu
        if event.button.id == "search":
            # Logic to perform search and display results
            self.app.pop_screen()  # go back to main menu