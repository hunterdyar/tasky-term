from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Header, Footer, Button, Static, Input
from textual.reactive import reactive


class TaskText(Input):
    """text"""


class Task(Static):
    complete = reactive(False)

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
        yield Button("[ ]", id="t-complete", variant="success")
        # focus on the new task once it is created, so we can just start typing.
        yield TaskText(placeholder="...start typing...", id="t-input").focus()

class TaskyTerm(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "tasky.tcss"
    BINDINGS = [
        ("n,a", "new_task", "New Task"),
        ("d,r", "delete_task", "Delete")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield ScrollableContainer(Task(), Task(), Task(), id="tasklist")

    def action_new_task(self) -> None:
        new_task = Task()
        self.query_one("#tasklist").mount(new_task)
        new_task.scroll_visible()


    def action_delete_task(self) -> None:
        # we need some way to keep track of which task we have highlighted.
        pass


if __name__ == "__main__":
    app = TaskyTerm()
    app.run()
