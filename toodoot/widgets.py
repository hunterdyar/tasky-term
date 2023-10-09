from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import Button, Static, Input, Label, TextArea, Rule
from textual import on, events


class ListItem(Static):
    md_item = None

    def deselect(self):
        self.remove_class("selected")
        self.add_class("deselected")

    def select(self):
        self.scroll_visible()
        self.add_class("selected")
        self.remove_class("deselected")

    def set_item(self, item):
        self.md_item = item

    def get_item(self):
        return self.md_item


class TaskWidget(ListItem):
    check = None
    edit_on_mount = False

    def __init__(self, task, edit_on_mount=False):
        super().__init__()
        self.set_item(task)
        self.edit_on_mount = edit_on_mount

    class IsUpdated(Message):
        pass  # pass in a class?
        # nothing special.

    def on_mount(self):
        self.scroll_visible()
        self.refresh_complete()
        self.refresh_text()
        self.query_one("#t-input").display = "none"
        self.query_one("#t-input").blur()

        if self.edit_on_mount:
            self.edit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "t-complete":
            self.md_item.complete = not self.md_item.complete
            self.refresh_complete()
            self.post_message(self.IsUpdated())

    def refresh_complete(self) -> None:
        box = self.query_one("#t-complete", CompleteBox)
        box.set_complete(self.md_item.complete)
        if self.md_item.complete:
            self.add_class("complete")
            self.query_one("#t-label", Static).add_class("complete")
        else:
            self.remove_class("complete")
            self.query_one("#t-label", Static).remove_class("complete")

    def refresh_text(self):
        self.query_one("#t-input", TextArea).load_text(self.md_item.text)
        self.query_one("#t-label", Static).update(self.md_item.text)

    def edit(self):
        inp = self.query_one("#t-input", TextArea)
        inp.display = "block"
        inp.focus()
        inp.action_cursor_line_end()
        self.query_one("#t-label").display = "none"

    def edit_finished(self):
        inp = self.query_one("#t-input", TextArea)
        self.md_item.text = inp.text
        self.refresh_text()
        inp.blur()  # free the cursor
        inp.display = "none"
        self.query_one("#t-label").display = "block"
        self.post_message(self.IsUpdated())

    def toggle(self):
        self.md_item.complete = not self.md_item.complete
        self.refresh_complete()

    @on(Input.Changed, "#t-input")
    def on_input_changed(self, m):
        self.task.text = m.value

    def compose(self) -> ComposeResult:
        yield CompleteBox(False, id="t-complete")
        # focus on the new task once it is created, so we can just start typing.
        yield Static(self.md_item.text, id="t-label")
        yield TaskText(_id="t-input").focus()


class CompleteBox(Static):
    complete = False

    def __init__(self, complete, id):
        super().__init__()
        self.id = id
        self.complete = complete

    def on_mount(self):
        self.set_complete(self.complete)

    def set_complete(self, complete):
        print("set complete " + str(complete))
        self.complete = complete
        if (self.complete):
            self.update("- \[x] ")
            self.add_class("complete")
        else:
            self.update("- [ ] ")
            self.remove_class("complete")


class TaskCategory(ListItem):
    is_first = True

    def __init__(self, header, is_first=True):
        super().__init__()
        self.set_item(header)
        self.is_first = is_first

    def compose(self) -> ComposeResult:
        if not self.is_first:
            yield Rule()
        yield Label(self.md_item.text)


class TaskText(TextArea):
    def __init__(self, _id):
        super().__init__(id=_id)
        self.show_line_numbers = False

    def _on_key(self, event: events.Key) -> None:
        if event.key == "enter" or event.key == "escape":
            self.parent.edit_finished()
            event.prevent_default()

    def action_cursor_down(self, select=False):
        # a different way of preventing multiple lines? we should move cursor to end/beginning of line
        pass

    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed):
        self.focus()  # If we move the mouse we lose focus but not really? odd bugs.
        print("this print wont be shown")

    def on_input_submitted(self):
        self.blur()
