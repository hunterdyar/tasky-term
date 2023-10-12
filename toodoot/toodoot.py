import os.path
import sys

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.widgets import Header, Footer

import markdowntasks
from widgets import TaskWidget
from widgets import TaskCategory


class TaskyTerm(App):
    CSS_PATH = "tasky.tcss"
    BINDINGS = [
        Binding(key="q", action="exit", description="Quit"),
        Binding(key="n,a", action="new_task", description="New"),
        Binding(key="e,enter", action="edit_task", description="Edit"),
        Binding(key="d,r", action="delete_task", description="Delete"),
        Binding(key="space", action="toggle", description="Check", show=True, key_display='_'),
        Binding(key="j,down,s", action="down", description="Scroll down", show=False),
        Binding(key="k,up,w", action="up", description="Scroll up", show=False),
    ]
    selected = 0
    elements = []
    md = markdowntasks.MDList()
    path = "todo.md"
    file_needs_created = False
    pathObj = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield ScrollableContainer(id="tasklist")

    def on_mount(self) -> None:
        # md could be stored in globals?
        self.file_needs_created = os.path.isfile(self.path)
        self.md.populate_from_file(self.path)
        l = self.query_one("#tasklist")
        is_first_cat = True
        for t in self.md.items:
            if isinstance(t, markdowntasks.mdTask):
                new_task = TaskWidget(t)
                l.mount(new_task)
                self.elements.append(new_task)
            elif isinstance(t, markdowntasks.mdHeader):
                new_header = TaskCategory(t, is_first_cat)
                l.mount(new_header)
                self.elements.append(new_header)
                is_first_cat = False

        if len(self.elements) > 0:
            self.selected_list_item().select()

        for e in self.elements[1:]:
            e.deselect()

        self.save()

    def action_new_task(self) -> None:
        # todo... insert the .mount at appropriate place in list
        # .mount takes an after property, index.
        if len(self.elements) == 0:
            new_task = TaskWidget(self.md.add_task(False, ""), edit_on_mount=True)
            self.query_one("#tasklist").mount(new_task)
            self.elements.append(new_task)
            # highlight First Task when creating it.
            self.select_element(new_task)
            return

        md_item = self.md.insert_task_after_item(self.elements[self.selected].md_item, False, "")
        new_task = TaskWidget(md_item, edit_on_mount=True)
        self.query_one("#tasklist").mount(new_task, after=self.elements[self.selected])
        self.elements.insert(self.selected + 1, new_task)
        # highlight First Task when creating it.
        self.select_element(new_task)

    def save(self):
        self.md.write_to_file(self.path)

    def on_key(self, event: events.Key) -> None:
        pass

    def action_edit_task(self):
        if len(self.elements) == 0:
            return
        list_item = self.selected_list_item()

        if isinstance(list_item, TaskWidget):
            list_item.edit()

    def action_toggle(self):
        if len(self.elements) == 0:
            return
        list_item = self.selected_list_item()

        if isinstance(list_item, TaskWidget):
            list_item.toggle()
            self.save()

    def action_exit(self):
        self.save()
        self.exit()

    def action_delete_task(self) -> None:
        if len(self.elements) == 0:
            return
        # we need some way to keep track of which task we have highlighted.
        list_item = self.selected_list_item()
        list_item.deselect()  # i guess?
        self.delete_item(list_item)

    def action_up(self):
        self.scroll_selected(-1)

    def action_down(self):
        self.scroll_selected(1)

    def scroll_selected(self, delta):
        l = len(self.elements)
        if l == 0:
            return
        prev = self.selected
        self.selected = self.selected + delta

        # Wrap
        if self.selected < 0:
            self.selected = l - 1
        if self.selected >= l:
            self.selected = 0

        # No change (only one item?)
        if self.selected == prev:
            return

        # deselect previous
        self.elements[prev].deselect()
        # select new
        self.selected_list_item().select()

    def select_element(self, task):
        index = self.elements.index(task)
        self.elements[self.selected].deselect()
        self.selected = index
        self.elements[self.selected].select()

    # could be a lamda?
    def selected_list_item(self):
        return self.elements[self.selected]

    def clear(self):
        # delete all tasks from #tasklist
        pass

    def delete_item(self, list_item):
        item = list_item.get_item()
        # remove from internal list, remove the item from the DOM, remove the task from the md ("database")
        self.elements.remove(list_item)
        list_item.remove()
        self.md.remove_item(item)
        # update selected
        # self.selected -= 1
        if self.selected >= len(self.elements):
            self.selected -= 1
        if self.selected < 0:
            self.selected = 0
        if 0 <= self.selected < len(self.elements):
            self.elements[self.selected].select()

        self.save()

    def on_task_widget_is_updated(self, message: TaskWidget.IsUpdated) -> None:
        print("dirty")
        self.save()


def main():
    if len(sys.argv) == 1:
        path = "todo.md"
    else:
        path = sys.argv[1]

    app = TaskyTerm()
    app.path = path
    app.run()
    if app.file_needs_created:
        print("Toodoot Edited "+str(app.pathObj))
    else:
        print("Toodoot Created "+str(app.pathObj))



if __name__ == "__main__":
    main()
