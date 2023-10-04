from textual import on, events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.widgets import Header, Footer, Button, Static, Input
import markdown_tasks
from widgets import TaskWidget, TaskCategory


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
        l = self.query_one("#tasklist")
        for t in self.md.items:
            if isinstance(t, markdown_tasks.mdTask):
                new_task = TaskWidget()
                new_task.set_task(t)
                l.mount(new_task)
            elif isinstance(t, markdown_tasks.mdHeader):
                new_header = TaskCategory()
                new_header.set_header(t)
                l.mount(new_header)
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
