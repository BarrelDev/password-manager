from textual.screen import Screen
from textual.widgets import Button, Label, DataTable, Static, Input
from textual.containers import Vertical, Horizontal
from rapidfuzz import process

from data import lock_session, get_dataframe, add_service, get_services, remove_service, get_credentials

class EntryList(Screen):
    def on_key(self, event):
        if event.key == "escape":
            lock_session()
            self.app.pop_screen()

    def compose(self):
        df = get_dataframe(self.app.fernet)

        header = Horizontal(
            Label("🔍 Entry List", id="title"),
            Button("➕ Add/❌ Remove Entry", id="add-entry"),
            Button("🔍 Search", id="search-entries"),
            Button("🔒", id="lock_button", tooltip="Lock"),
            id="header"
        )

        # This would be populated with actual entries
        if not df.empty:
            self.table = DataTable(id="table")
            self.table.cursor_type = "row"
            _, _, self.password_key = self.table.add_columns("Service", "Username", "Password")
            masked = "••••••"
            self.real_passwords = {}  # Store real passwords for later use
            for _, row in df.iterrows():
                key = self.table.add_row(row["service"], row["usrname"], masked)
                self.real_passwords[key] = row["passwd"]
            self.table.focus()
            yield Vertical(
                header,
                self.table,
                id="list-container"
            )
        else:
            yield Vertical(
                header,
                Label("No entries available yet.", id="entries"),
                id="list-container"
            )

    def on_data_table_row_highlighted(self, event) -> None:
        # Mask all passwords
        for row_key in self.real_passwords:
            self.table.update_cell(row_key, self.password_key, "••••••")

        # Reveal the highlighted password
        highlighted_key = event.row_key
        real_password = self.real_passwords.get(highlighted_key)
        if real_password is not None:
            self.table.update_cell(highlighted_key, self.password_key, real_password)

    def on_button_pressed(self, event):
        match event.button.id:
            case "add-entry":
                self.app.push_screen(AddEntry())
            case "search-entries":
                self.app.push_screen(Search())
            case "lock_button":
                lock_session()
                self.app.pop_screen()
        

    def on_mount(self):
        # Load entries from data source and display them
        pass  # Implement loading logic here

class AddEntry(Screen):
    def on_key(self, event):
        if event.key == "escape":
            self.app.pop_screen()
    
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
        self.table.cursor_type = "row"
        _, _, self.password_key = self.table.add_columns("Service", "Username", "Password")
        masked = "••••••"
        self.real_passwords = {}  # Store real passwords for later use
        for _, row in self.df.iterrows():
            key = self.table.add_row(row["service"], row["usrname"], masked)
            self.real_passwords[key] = row["passwd"]

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
                key = self.table.add_row(service, username, "••••••")
                self.real_passwords[key] = password  # Store real password


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
                    self.real_passwords.pop(row_key, None)  # Remove from real passwords
                    self.table.remove_row(row_key)
                    self.query_one("#message", Static).update("🗑️ Entry removed.")
                else:
                    self.query_one("#message", Static).update("⚠️ Select a row to remove.")

            case "back":
                self.app.pop_screen()

class Search(Screen):
    def on_key(self, event):
        if event.key == "escape":
            self.app.pop_screen()

    def compose(self):
        self.real_passwords = {}  # Store real passwords for later use
        self.table = DataTable(id="search-results")
        _, _, self.password_key, _ = self.table.add_columns("Service", "Username", "Password", "Score")
        self.table.cursor_type = "row"

        yield Vertical(
            Horizontal(
                Label("🔍 Search Entries", id="title"),
                Button("Back to Main Menu", id="back"),
                id="header"),
            Horizontal(
                Input(placeholder="Search by service name", id="search-input").focus(),
                Button("Search", id="search"),
                id="search-controls"
            ),
            self.table,
            id="main-layout"
        )

    def on_button_pressed(self, event):
        if event.button.id == "back":
            self.app.pop_screen()  # go back to main menu
        if event.button.id == "search":
            self.submit_search()

    def on_input_submitted(self, event: Input.Submitted) -> None:
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
        for service, score, _ in results:
            username, password = get_credentials(self.app.fernet, service)
            key = self.query_one("#search-results", DataTable).add_row(service, username, password, score)
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