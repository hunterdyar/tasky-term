from pathlib import Path
from sys import argv
import mistune
from mistune import BlockState
from mistune.renderers.markdown import MarkdownRenderer
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Footer, RichLog
from textual.widgets._data_table import CellDoesNotExist

import md_task_lists
import TasklistMarkdownRenderer


class TaskText(RichLog):
    row_key = ""
    def __init__(self, task_text):
        super().__init__()
        self.text = task_text

    def on_mount(self) -> None:
        self.style = "#cccccc"
        self.justify = "left"
        self.max_lines = 1

class TableApp(App):
    BINDINGS = [
        Binding(key="q", action="exit", description="Quit"),
        Binding(key="n", action="new_task", description="New"),
        Binding(key="e", action="edit", description="Edit"),
        Binding(key="d", action="delete", description="Delete"),
        Binding(key="space", action="toggle", description="Check", show=True, key_display='_'),
        Binding(key="j", action="down", description="Scroll down", show=False),
        Binding(key="k", action="up", description="Scroll up", show=False),
    ]
    path = "demo.md"
    md = mistune.create_markdown(renderer=None, plugins=['task_lists'])
    # mistune.import_plugin('md_task_lists.md_task_lists')
    md_render = mistune.create_markdown(renderer=MarkdownRenderer)
    tokens = None
    table = None
    task_col_key = "tasks"
    complete_col_key = "complete"
    row_to_element = {}

    def compose(self) -> ComposeResult:
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        self.table = self.query_one(DataTable)
        self.table.cursor_type = "row"
        self.table.zebra_stripes = True
        self.add_title_columns()
        self.set_table_from_file()

    def add_title_columns(self):
        self.table.add_column("X", width=3, key=self.complete_col_key)
        self.table.add_column(Text("Task", justify="center"), key=self.task_col_key)  # centers the label 'task'.

    def find_tasks_recursive(self, element, parent=None):
        # we gottta go deeper
        if isinstance(element, list):
            for each_element in element:
                self.find_tasks_recursive(each_element, parent=element)
            return

        # While walking the tree, we store a reference to the parent.

        if element['type'] == 'task_list_item':
            element['parent'] = parent
            tt = TaskText(str(element['children'][0]['children'][0]['raw']))
            styled_row = [
                element['attrs']['checked'],
                tt
            ]
            key = self.table.add_row(*styled_row)
            tt.row_key = key
            self.row_to_element[key] = element

        if element['type'] == 'list':
            for child in element['children']:
                self.find_tasks_recursive(child, parent=element)

        # So we keep the tokens list intact. They are classes - lists.
        # We reference the token in the class, and modify the markdown token when we edit the task.
        # Then.... saving is just rendering the tokens.

    def set_table_from_file(self):
        with open(self.path, encoding="utf-8") as f:
            self.table.clear()
            data = f.read()
            self.tokens = self.md.parse(data)[0]
            self.find_tasks_recursive(self.tokens)
        # for testing
        self.create_task()

    def save(self):
        print("save")
        with open(self.path, 'w', encoding="utf-8") as f:
            r = TasklistMarkdownRenderer.TaskListMarkdownRenderer()

            # this ... might do nothing?
            r.register('task_list_item', md_task_lists.md_render_task_list_item)

            m = r.render_tokens(self.tokens, BlockState())
            f.write(m)
            f.close()

    def delete_task(self, row_key):
        # todo if is row key
        self.table.remove_row()
        e = self.row_to_element[row_key]
        # you ever write code that you just _feel_ is wrong? in your bones?
        e['parent']['children'].remove(e)

    def get_first_list(self, tokens):
        if isinstance(tokens, list):
            for c in tokens:
                x = self.get_first_list(c)
                if x is not None:
                    return x
        if 'type' in tokens:
            if tokens['type'] == 'list':
                return tokens
            elif 'children' in tokens:
                for tok in tokens['children']:
                    l = self.get_first_list(tok)
                    if l is not None:
                        return
                    else:
                        return None
        return None

    def create_task(self):
        # selected = self.selected_row()
        l = None
        # if selected is None:
        l = self.get_first_list(self.tokens)
        if l is None:
            # Create an empty List.
            l = {'type': 'list', 'children': [],
                 'tight': True, 'bullet': '-', 'attrs': {'depth': 0, 'ordered': False}}
            self.tokens.append(l)

        text = "banana"

        token = {'type': 'task_list_item',
                 'children': [{'type': 'block_text', 'children': [{'type': 'text', 'raw': text}]}],
                 'attrs': {'checked': False}, 'parent': l}
        l['children'].append(token)

        # todo: handle style and checkmark cell classes. THis will let us handle mouse input on the check.
        tt = TaskText()
        tt.text = str(text)
        tt.complete = False
        r = [
            False,
            tt
        ]
        key = self.table.add_row(*r)
        self.row_to_element[key] = token

    def toggle_edit(self, rowkey):
        cell = self.table.get_cell(rowkey, self.task_col_key)
        cell.edit()

    def action_new_task(self):
        self.create_task()
        self.save()

    def action_down(self):
        table = self.table
        table.move_cursor(row=table.cursor_row + 1, animate=False)

    def action_up(self):
        table = self.table
        table.move_cursor(row=table.cursor_row - 1, animate=False)

    def action_toggle(self):
        table = self.table
        row = self.selected_row()
        if table.row_count == 0:
            return
        checked = table.get_cell(row, self.complete_col_key)
        checked = not checked
        table.update_cell(row, self.complete_col_key, checked)
        self.row_to_element[row]['attrs']['checked'] = checked
        self.save()

    def action_delete(self):
        table = self.table
        try:
            row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
            self.delete_task(row_key)
            self.save()
        except CellDoesNotExist:
            # Can't delete no thing... this is fine tho.
            # It feels gross to catch this in error instead of checking it before calling.
            pass

    def action_edit(self):
        table = self.table
        try:
            row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
            self.toggle_edit(row_key)
        except CellDoesNotExist:
            pass

    def action_exit(self):
        print("goodbye")
        self.save()
        quit()

    def selected_row(self):
        table = self.query_one(DataTable)
        # todo: if empty check
        if table.row_count == 0:
            return None
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        return row_key


# largely takes the code from the _list.py file, which skips calling on list_items (so skips task list items), and injects that bit.


app = TableApp()
if __name__ == "__main__":
    if len(argv) > 1 and Path(argv[1]).exists():
        app.path = Path(argv[1])
    app.run()
