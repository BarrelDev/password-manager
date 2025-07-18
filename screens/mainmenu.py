from textual.screen import Screen
from textual.widgets import Button, Label, DataTable, Static, Input
from textual.containers import Vertical, Horizontal

from data import lock_session, get_dataframe, write_dataframe, add_service, get_services, remove_service

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
    BINDINGS = [("escape", "app.pop_screen", "Back")]
    
    def compose(self):
        self.df = get_dataframe(self.app.fernet)

        # Input fields row
        input_row = Horizontal(
            Input(placeholder="Service", id="service-input"),
            Input(placeholder="Username", id="username-input"),
            Input(placeholder="Password", password=True, id="password-input"),
            Button("Add Entry", id="add"),
            id="input-fields"
        )

        # Populate the table
        self.table = DataTable(id="entry-table")
        self.table.add_columns("Service", "Username", "Password")
        for _, row in self.df.iterrows():
            self.table.add_row(row["service"], row["usrname"], row["passwd"])

        # Control buttons
        button_row = Horizontal(
            Button("Remove Selected", id="remove"),
            Button("Back to Main Menu", id="back"),
            id="buttons"
        )

        yield Vertical(
            Label("➕ Add / ❌ Remove Entries", id="title"),
            input_row,
            self.table,
            button_row,
            Static("", id="message"),
            id="main-layout"
        )

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
                self.table.add_row(service, username, password)

                # Clear inputs and notify
                for field_id in ["#service-input", "#username-input", "#password-input"]:
                    self.query_one(field_id, Input).value = ""
                self.query_one("#message", Static).update("✅ Entry added.")

            case "remove":
                if self.table.cursor_row is not None:
                    index = self.table.cursor_row
                    self.df = self.df.drop(self.df.index[index]).reset_index(drop=True)
                    remove_service(self.app.fernet, self.table.get_row_at(index)[0])
                    row_key, _ = self.table.coordinate_to_cell_key(self.table.cursor_coordinate)
                    self.table.remove_row(row_key)
                    self.query_one("#message", Static).update("🗑️ Entry removed.")
                else:
                    self.query_one("#message", Static).update("⚠️ Select a row to remove.")

            case "back":
                self.app.pop_screen()

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