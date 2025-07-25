from textual.screen import Screen
from textual.widgets import Button, Label, DataTable, Static, Input
from textual.containers import Vertical, Horizontal
from textual import log
from rapidfuzz import process
import time

from data import lock_session, get_dataframe, add_service, get_services, remove_service, get_credentials

class EntryList(Screen):
    def on_key(self, event):
        if self.app.screen_stack[-1] != self:
            return  # Don't respond if not top screen
        key = event.key

        # Escape to lock & exit
        if key == "escape" or key == "q":
            lock_session()
            self.app.pop_screen()
            return

        if key == "j":
            self.table.action_cursor_down()
        elif key == "k":
            self.table.action_cursor_up()
        elif key == "g":  # Go to top
            self.table.cursor_coordinate = (0, 0)
        elif key == "G":  # Go to bottom
            if self.table.row_count > 0:
                self.table.cursor_coordinate = (self.table.row_count - 1, 0)
        elif key == "a" or key == "i":
            self.app.push_screen("add")
        elif event.character == "/":
            self.app.push_screen("search")
        elif event.key == "r":
            if self.table.cursor_row is not None:
                self.prompt_replace(self.table.cursor_row)
        elif key == "d":
            # Vim-style 'dd' to delete
            if self._vim_delete_mode:
                self._vim_delete_mode = False
                self._delete_current_row()
            else:
                self._vim_delete_mode = True
                self.set_timer(0.5, self._reset_vim_delete_mode)
        else:
            self._vim_delete_mode = False  # Reset on other keys

    def _reset_vim_delete_mode(self):
        self._vim_delete_mode = False

    def _delete_current_row(self):
        if self.table.cursor_row is not None and not self.df.empty:
            index = self.table.cursor_row
            self.df = self.df.drop(self.df.index[index]).reset_index(drop=True)
            remove_service(self.app.fernet, self.table.get_row_at(index)[0])
            row_key, _ = self.table.coordinate_to_cell_key(self.table.cursor_coordinate)
            self.real_passwords.pop(row_key, None)  # Remove from real passwords
            self.table.remove_row(row_key)
        if self.df.empty:
            self.table.clear()
            self.table.add_row("No entries available yet.", "", "")

    def prompt_replace(self, index):
        service = self.df.iloc[index]["service"]
        current_username = self.df.iloc[index]["usrname"]

        outer_self = self
        
        def after_input(self, input_type, new_value):
            if not new_value:
                return

            if input_type == "username":
                self.df.at[index, "usrname"] = new_value
            elif input_type == "password":
                self.df.at[index, "passwd"] = new_value

            # Save back to encrypted storage
            update_username = self.df.at[index, "usrname"]
            update_password = self.df.at[index, "passwd"]
            remove_service(self.app.fernet, service)  # Remove old entry
            add_service(self.app.fernet, service, update_username, update_password)

            self.refresh_table()

        # Ask: username or password?
        def prompt_field_choice(self):
            from textual.widgets import OptionList
            from textual.widgets.option_list import Option
            from textual.screen import ModalScreen

            outer_self = self

            class FieldChoiceScreen(ModalScreen):
                def compose(inner_self):
                    inner_self.optionlist = OptionList(
                        Option("Update Username", id="username"),
                        Option("Update Password", id="password"),
                        id="choice-list"
                    )
                    yield inner_self.optionlist

                def on_mount(inner_self):
                    inner_self.optionlist.focus()

                def on_key(self, event):
                    key = event.key

                    # Escape to lock & exit
                    if key == "escape" or key == "q":
                        self.app.pop_screen()
                        return

                    if key == "j":
                        self.optionlist.action_cursor_down()
                    elif key == "k":
                        self.optionlist.action_cursor_up()

                def on_option_list_option_selected(inner_self, event):
                    field = event.option.id
                    self.app.pop_screen()
                    prompt_new_value(outer_self, field)

            self.app.push_screen(FieldChoiceScreen())

        # Ask for new value
        def prompt_new_value(self, input_type):
            from textual.widgets import Input
            from textual.screen import ModalScreen

            class InputScreen(ModalScreen):
                def compose(inner_self):
                    placeholder = f"New {input_type.capitalize()}"
                    yield Input(placeholder=placeholder, password=(input_type == "password"), id="new_input")

                def on_input_submitted(inner_self, event):
                    value = event.value.strip()
                    self.app.pop_screen()
                    after_input(self, input_type, value)

            self.app.push_screen(InputScreen())

        prompt_field_choice(outer_self)


    def compose(self):
        self.df = get_dataframe(self.app.fernet)
        self._vim_delete_mode = False  # Vim delete mode flag

        header = Horizontal(
            Label("🔍 Entry List", id="title"),
            Button("➕ Add Entry", id="add-entry"),
            Button("❌ Remove Selected", id="remove-entry"),
            Button("🔍 Search", id="search-entries"),
            Button("🔒", id="lock_button", tooltip="Lock"),
            id="header"
        )

        # This would be populated with actual entries
        if not self.df.empty:
            self.table = DataTable(id="table")
            self.table.cursor_type = "row"
            _, _, self.password_key = self.table.add_columns("Service", "Username", "Password")
            masked = "••••••"
            self.real_passwords = {}  # Store real passwords for later use
            for _, row in self.df.iterrows():
                key = self.table.add_row(row["service"], row["usrname"], masked)
                self.real_passwords[key] = row["passwd"]
            self.table.focus()
        else:
            self.table = DataTable(id="table")
            self.table.cursor_type = "row"
            _, _, self.password_key = self.table.add_columns("Service", "Username", "Password")
        yield Vertical(
            header,
            self.table,
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
                self.app.push_screen("add")
                self.refresh_table()
            case "search-entries":
                self.app.push_screen("search")
            case "remove-entry":
                self._delete_current_row()
            case "lock_button":
                lock_session()
                self.app.pop_screen()
    
    def on_screen_resume(self):
        # Refresh the table with the latest data when returning to this screen
        self.refresh_table()

    def on_mount(self):
        self.table = self.query_one("#table", DataTable)
        self.refresh_table()

    def refresh_table(self):
        self.df = get_dataframe(self.app.fernet)

        self.table.clear()
        self.real_passwords = {}

        if self.df.empty:
            self.table.add_row("No entries available yet.", "", "")
            return

        masked = "••••••"
        for _, row in self.df.iterrows():
            key = self.table.add_row(row["service"], row["usrname"], masked)
            self.real_passwords[key] = row["passwd"]
        self.table.focus()


class AddEntry(Screen):
    def on_key(self, event):
        if event.key == "escape" or event.key == "q":
            self.app.pop_screen()
    
    def on_mount(self):
        self.query_one("#service-input", Input).focus()

    def on_screen_resume(self):
        self.query_one("#service-input", Input).focus()

    def compose(self):
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

                # Clear inputs and notify
                for field_id in ["#service-input", "#username-input", "#password-input"]:
                    self.query_one(field_id, Input).value = ""
                self.query_one("#message", Static).update("✅ Entry added.")
                self.query_one("#service-input", Input).focus()

            case "back":
                self.app.pop_screen()

class Search(Screen):
    def on_key(self, event):
        if event.key == "escape" or event.key == "q":
            self.app.pop_screen()

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