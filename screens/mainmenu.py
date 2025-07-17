from textual.screen import Screen
from textual.widgets import Button, Label
from textual.containers import Vertical

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
            self.app.push_screen("entry_list")
        elif event.button.id == "add":
            self.app.push_screen("add_entry")
        elif event.button.id == "lock":
            self.app.pop_screen()  # go back to login