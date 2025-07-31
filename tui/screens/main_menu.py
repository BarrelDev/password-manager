from textual.screen import Screen
from textual.widgets import Button, Label, DataTable
from textual.containers import Vertical, Horizontal
import pyperclip

from core.data import get_dataframe, add_service, remove_service
from core.session import lock_session
from tui.screens.modals import InputPromptScreen, FieldChoiceScreen

class EntryList(Screen):
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
            Label("↵ to copy | ⎋ to lock | / to search | a/i to add | r to replace | ctrl+q to close", id="footer"),
            id="list-container"
        )

    def on_mount(self):
        self.table = self.query_one("#table", DataTable)
        self._refresh_table()

    def on_screen_resume(self):
        # Refresh the table with the latest data when returning to this screen
        self._refresh_table()

    def on_key(self, event):
        if self.app.screen_stack[-1] != self:
            return  # Don't respond if not top screen
        key = event.key

        match key:
            # Escape to lock & exit
            case "escape" | "q":
                lock_session()
                self.app.pop_screen()
                return
            # Vim-style navigation
            case "j":
                self.table.action_cursor_down()
            case "k":
                self.table.action_cursor_up()
            case "g":  # Go to top
                self.table.cursor_coordinate = (0, 0)
            case "G":  # Go to bottom
                if self.table.row_count > 0:
                    self.table.cursor_coordinate = (self.table.row_count - 1, 0)
            case "a" | "i":
                self.app.push_screen("add")
            case "/":
                self.app.push_screen("search")
            case "r":
                if self.table.cursor_row is not None:
                    self._prompt_replace(self.table.cursor_row)
            case "enter":
                self._copy_selected_password()
            case "d":  # Vim-style 'dd' to delete
                if self._vim_delete_mode:
                    self._vim_delete_mode = False
                    self._delete_current_row()
                else:
                    self._vim_delete_mode = True
                    self.set_timer(0.5, self._reset_vim_delete_mode)
            case _:
                self._vim_delete_mode = False  # Reset on other keys

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
                self._refresh_table()
            case "search-entries":
                self.app.push_screen("search")
            case "remove-entry":
                self._delete_current_row()
            case "lock_button":
                lock_session()
                self.app.pop_screen()

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

    def _copy_selected_password(self):
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

    def _prompt_replace(self, index):
        service = self.df.iloc[index]["service"]
        username = self.df.iloc[index]["usrname"]

        def after_field_selected(field):
            def after_value_entered(value):
                if not value:
                    return
                if field == "username":
                    self.df.at[index, "usrname"] = value
                elif field == "password":
                    self.df.at[index, "passwd"] = value

                # Save updated credentials
                remove_service(self.app.fernet, service)
                add_service(
                    self.app.fernet,
                    service,
                    self.df.at[index, "usrname"],
                    self.df.at[index, "passwd"],
                )
                self._refresh_table()

            self.app.push_screen(
                InputPromptScreen(
                    placeholder=f"New {field.capitalize()}",
                    password=(field == "password"),
                    on_submit=after_value_entered,
                )
            )

        self.app.push_screen(FieldChoiceScreen(after_field_selected))

    def _refresh_table(self):
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