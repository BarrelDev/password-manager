from textual.screen import ModalScreen
from textual.widgets import OptionList, Input
from textual.widgets.option_list import Option

class FieldChoiceScreen(ModalScreen):
    def __init__(self, on_selected):
        super().__init__()
        self.on_selected = on_selected

    def compose(self):
        self.optionlist = OptionList(
            Option("Update Username", id="username"),
            Option("Update Password", id="password"),
        )
        yield self.optionlist

    def on_mount(self):
        self.optionlist.focus()

    def on_option_list_option_selected(self, event):
        self.app.pop_screen()
        self.on_selected(event.option.id)

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

class InputPromptScreen(ModalScreen):
    def __init__(self, placeholder, password, on_submit):
        super().__init__()
        self.placeholder = placeholder
        self.password = password
        self.on_submit = on_submit

    def compose(self):
        yield Input(placeholder=self.placeholder, password=self.password, id="prompt_input")

    def on_input_submitted(self, event):
        self.app.pop_screen()
        self.on_submit(event.value.strip())