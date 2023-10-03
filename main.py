from textual import on, events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.events import DescendantBlur
from textual.widgets import Header, Footer, Button, Static, Input
from textual.reactive import reactive
import markdown_tasks
class TaskText(Input):
    """text"""
    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed):
        self.focus()  # If we move the mouse we lose focus but not really? odd bugs.
        print("this print wont be shown")

    def on_input_submitted(self):
        self.blur()


class Task(Static):
    complete = reactive(False)
    text = reactive(str)

    def on_mount(self):
        self.scroll_visible()
        self.query_one("#t-complete").text = self.text
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

    def watch_text(self, text):
        print("watch text changed")
        #self.query_one("#t-input", TaskText).input = text

    def compose(self) -> ComposeResult:
        yield Button("[ ]", id="t-complete", variant="primary")
        # focus on the new task once it is created, so we can just start typing.
        yield TaskText(placeholder="...start typing...", id="t-input").focus()


class TaskyTerm(App):
    CSS_PATH = "tasky.tcss"
    BINDINGS = [
        Binding(key="q", action="exit", description="Quit"),
        Binding(key="n,a", action="new_task", description="New"),
        Binding(key="e,enter", action="edit_task", description="Edit"),
        Binding(key="d,r", action="delete_task", description="Delete"),
        Binding(key="space", action="toggle", description="Check", show=True, key_display='_'),
        Binding(key="j", action="down", description="Scroll down", show=False),
        Binding(key="k", action="up", description="Scroll up", show=False),
    ]
    selected = 0
    md = markdown_tasks.MDList()
    tokens = None
    path = "demo.md"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield ScrollableContainer(id="tasklist")

    def on_mount(self) -> None:
        self.md.populate_from_file(self.path)
        for t in self.md.get_tasks():
            Task()

    def action_new_task(self) -> None:
        new_task = Task() # todo
        self.query_one("#tasklist").mount(new_task)

    def on_key(self, event: events.Key) -> None:
        pass

    def action_delete_task(self) -> None:
        # we need some way to keep track of which task we have highlighted.
        pass

    def clear(self):
        # delete all tasks from #tasklist
        pass

if __name__ == "__main__":
    app = TaskyTerm()
    app.run()
