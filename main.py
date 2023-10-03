from textual import on, events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.events import DescendantBlur
from textual.message import Message
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


class TaskWidget(Static):
    task = None

    class IsUpdated(Message):
        t = None
        # nothing special.

    def on_mount(self):
        self.scroll_visible()
        self.refresh_complete()
        self.refresh_text()

    # I don't know if this is doing anything.

    @on(DescendantBlur)
    def on_descendant_blur(self, widget):
        self.blur()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "t-complete":
            self.task.complete = not self.task.complete
            self.add_class("complete") if self.task.complete else self.remove_class("complete")
            self.refresh_complete()
            self.post_message(self.IsUpdated())

    def refresh_complete(self) -> None:
        if self.task.complete:
            self.query_one("#t-complete", Button).label = "\[x]"
        else:
            self.query_one("#t-complete", Button).label = "[ ]"

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
        # md could be stored in globals?
        self.md.populate_from_file(self.path)
        print('mount'+str(len(self.md.get_tasks())))
        for t in self.md.get_tasks():
            new_task = TaskWidget()
            new_task.set_task(t)
            self.query_one("#tasklist").mount(new_task)
        self.save()

    def action_new_task(self) -> None:
        new_task = TaskWidget()
        new_task.set_task(self.md.add_task(False,""))
        self.query_one("#tasklist").mount(new_task)
        self.save()

    def save(self):
        self.md.write_to_file(self.path)

    def on_key(self, event: events.Key) -> None:
        pass

    def action_delete_task(self) -> None:
        # we need some way to keep track of which task we have highlighted.
        pass

    def clear(self):
        # delete all tasks from #tasklist
        pass

    def on_task_widget_is_updated(self,message: TaskWidget.IsUpdated)->None:
        print("dirty")
        self.save()

if __name__ == "__main__":
    app = TaskyTerm()
    app.run()
