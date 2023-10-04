from textual.app import ComposeResult
from textual.events import DescendantBlur
from textual.message import Message
from textual.widgets import Button, Static, Input, Label
from textual import on

class TaskCategory(Static):
    header = None

    def __init__(self,header):
        super().__init__()
        self.set_header(header)
    def compose(self) -> ComposeResult:
        yield Label(self.header.text)

    def set_header(self, header):
        self.header = header


class TaskText(Input):
    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed):
        self.focus()  # If we move the mouse we lose focus but not really? odd bugs.
        print("this print wont be shown")

    def on_input_submitted(self):
        self.blur()


class TaskWidget(Static):
    task = None
    check = None

    def __init__(self, task):
        super().__init__()
        self.set_task(task)

    class IsUpdated(Message):
        t = None
        # nothing special.

    def on_mount(self):
        self.scroll_visible()
        self.refresh_complete()
        self.refresh_text()

    @on(DescendantBlur)
    def on_descendant_blur(self, widget):
        self.blur()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "t-complete":
            self.task.complete = not self.task.complete
            self.refresh_complete()
            self.post_message(self.IsUpdated())

    def refresh_complete(self) -> None:
        if self.task.complete:
            self.query_one("#t-complete", Button).label = "\[x]"
            self.add_class("complete")
        else:
            self.query_one("#t-complete", Button).label = "[ ]"
            self.remove_class("complete")

    def refresh_text(self):
        self.query_one("#t-input", TaskText).value = self.task.text

    @on(Input.Changed,"#t-input")
    def on_input_changed(self, m):
        self.task.text = m.value

    @on(Input.Changed,"#t-input")
    def on_input_submitted(self, m):
        self.post_message(self.IsUpdated())

    def compose(self) -> ComposeResult:
        yield Button("[ ]", id="t-complete", variant="primary")
        # focus on the new task once it is created, so we can just start typing.
        yield TaskText(placeholder="...start typing...", id="t-input").focus()

    def set_task(self, task):
        self.task = task