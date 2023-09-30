from textual import on, events
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.events import DescendantBlur
from textual.widgets import Header, Footer, Button, Static, Input
from textual.reactive import reactive


class TaskText(Input):
    """text"""

    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed):
        self.focus() # If we move the mouse we lose focus but not really? odd bugs.
        print("this print wont be shown")

    def on_input_submitted(self):
        self.blur()


class Task(Static):
    complete = reactive(False)

    # I don't know if this is doing anything.
    @on(DescendantBlur)
    def on_descendant_blur(self, widget):
        self.blur()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "t-complete":
            self.complete = not self.complete
            self.add_class("complete") if self.complete else self.remove_class("complete")

    def watch_complete(self, complete: bool) -> None:
        if self.complete:
            self.query_one("#t-complete", Button).label = "\[x]"
        else:
            self.query_one("#t-complete", Button).label = "[ ]"

    def compose(self) -> ComposeResult:
        yield Button("[ ]", id="t-complete", variant="primary")
        # focus on the new task once it is created, so we can just start typing.
        yield TaskText(placeholder="...start typing...", id="t-input").focus()


class TaskyTerm(App):
    selected = 0

    CSS_PATH = "tasky.tcss"
    BINDINGS = [
        ("n,a", "new_task", "New Task"),
        ("d,r", "delete_task", "Delete")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield ScrollableContainer(id="tasklist")

    def action_new_task(self) -> None:
        new_task = Task()
        self.query_one("#tasklist").mount(new_task)  # todo move this to on_mount
        new_task.scroll_visible()

    def on_key(self, event: events.Key) -> None:
        pass

    def action_delete_task(self) -> None:
        # we need some way to keep track of which task we have highlighted.
        pass


if __name__ == "__main__":
    app = TaskyTerm()
    app.run()
