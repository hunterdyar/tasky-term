from itertools import cycle
from pathlib import Path
from sys import argv
from typing import Dict, Any
import mistune
from mistune import BlockState
from mistune.renderers.markdown import MarkdownRenderer
from mistune.util import strip_end
from rich.text import Text
from textual.app import App, ComposeResult
from textual.coordinate import Coordinate
from textual.reactive import var
from textual.widgets import DataTable
import md_task_lists

ROWS = [
    (True, "Joseph Schooling"),
    (False, "Michael Phelps"),
    (False, "Chad le Clos"),
    (False, "László Cseh"),
    (True, "Li Zhuhao"),
    (False, "Mehdy Metella"),
    (False, "Tom Shields"),
    (True, "Aleksandr Sadovnikov"),
    (True, "Darren Burns"),
]


class TableApp(App):
    path = "demo.md"
    md = mistune.create_markdown(renderer=None, plugins=['task_lists'])
    # mistune.import_plugin('md_task_lists.md_task_lists')
    md_render = mistune.create_markdown(renderer=MarkdownRenderer)
    tokens = None
    table = None
    complete_col_key = "complete"
    row_to_element = {}

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        self.table = self.query_one(DataTable)
        self.table.cursor_type = "row"
        self.table.zebra_stripes = True
        self.add_title_columns()
        # self.table.add_rows(ROWS[1:])
        # todo: styled columns instead of rows. And instead of Text, we make our own Complete and TaskText types
        for row in ROWS[0:]:
            # Adding styled and justified `Text` objects instead of plain strings.
            styled_row = [
                Text(str(cell), style="#cccccc", justify="left") for cell in row
            ]
            self.table.add_row(*styled_row)
        self.set_table_from_file()

    def add_title_columns(self):
        self.table.add_column("X", width=3, key=self.complete_col_key)
        self.table.add_column(Text("Task", justify="center"))  # centers the label 'task'.

    def find_tasks_recursive(self, element):
        # we gottta go deeper
        if isinstance(element, list):
            for each_element in element:
                self.find_tasks_recursive(each_element)
            return

        if element['type'] == 'task_list_item':
            styled_row = [
                element['attrs']['checked'],
                Text(str(element['children'][0]['children'][0]['raw']), style="#cccccc", justify="left")
            ]
            key = self.table.add_row(*styled_row)
            self.row_to_element[key] = element

        if element['type'] == 'list':
            for child in element['children']:
                self.find_tasks_recursive(child)

        # So we keep the tokens list intact. They are classes - lists.
        # We reference the token in the class, and modify the markdown token when we edit the task.
        # Then.... saving is just rendering the tokens.

    def set_table_from_file(self):
        with open(self.path, encoding="utf-8") as f:
            self.table.clear()
            data = f.read()
            self.tokens = self.md.parse(data)[0]
            liopen = False

            self.find_tasks_recursive(self.tokens)

            styled_row = [
                # completed, Text(str(token.content[3:]), style="#cccccc", justify="left")
            ]
            self.table.add_row(*styled_row)

        self.save()

    def save(self):
        print("save")
        with open(self.path, 'w', encoding="utf-8") as f:
            r = ReMarkdown()
            # this isn't working
            r.register('task_list_item', md_task_lists.md_render_task_list_item)

            #md_task_lists.md_task_token_process(self.tokens)

            #m = self.tokens[0][3]['children'][0]['type']+"\n\n"
            #= renderer.render_token(self.tokens[0][3]['children'][0], state=BlockState())

            m = r.render_tokens(self.tokens, BlockState())
            # m = renderer(self.tokens[0], state=BlockState())
            f.write(m)
            f.close()

    def key_c(self):
        table = self.table
        table.move_cursor(row=table.cursor_row + 1, animate=False)

    def key_space(self):
        table = self.table
        row = self.selected_row()
        if table.row_count == 0:
            return
        checked = table.get_cell(row, self.complete_col_key)
        checked = not checked
        table.update_cell(row, self.complete_col_key, checked)
        self.row_to_element[row]['attrs']['checked'] = checked
        self.save()

    def key_d(self):
        table = self.table
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        table.remove_row(row_key)

    def selected_row(self):
        table = self.query_one(DataTable)
        # todo: if empty check
        if table.row_count == 0:
            return None
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        return row_key


class ReMarkdown(MarkdownRenderer):
    def render_token(self, token, state):
        print('render token: '+token['type'])
        func = self._get_method(token['type'])
        # hack workaround for register not working?
        if token['type'] == 'task_list_item':
            func=self.render_task_list_item

        return func(token, state)
    def render_task_list_item(self, token: Dict[str, Any], state: BlockState) -> str:
        print("Render task list item remarkdown")
        check = "[x]" if token.get('attrs').get('checked') else "[ ]"
        return check + " " + self.render_children(token, state)

    def list(self, token: Dict[str, Any], state: BlockState) -> str:
        return self.render_list(token, state)

    def render_list(self, token, state) -> str:
        attrs = token['attrs']
        if attrs['ordered']:
            children = self._render_ordered_list(token, state)
        else:
            children = self._render_unordered_list(token, state)

        text = ''.join(children)
        parent = token.get('parent')
        if parent:
            if parent['tight']:
                return text
            return text + '\n'
        return strip_end(text) + '\n'

    def _render_list_item(self, parent, item, state):
        leading = parent['leading']
        text = ''

        if item['type'] == 'task_list_item':
            check = "[x] " if item['attrs'].get('checked') else "[ ] "
            text += check

        for tok in item['children']:
            if tok['type'] == 'list':
                tok['parent'] = parent
            elif tok['type'] == 'blank_line':
                continue
            text += self.render_token(tok, state)

        lines = text.splitlines()
        text = (lines[0] if lines else '') + '\n'
        prefix = ' ' * len(leading)
        for line in lines[1:]:
            if line:
                text += prefix + line + '\n'
            else:
                text += '\n'
        return leading + text

    def _render_ordered_list(self, token, state):
        attrs = token['attrs']
        start = attrs.get('start', 1)
        for item in token['children']:
            leading = str(start) + token['bullet'] + ' '
            parent = {
                'leading': leading,
                'tight': token['tight'],
            }
            yield self._render_list_item(parent, item, state)
            start += 1

    def _render_unordered_list(self, token, state):
        parent = {
            'leading': token['bullet'] + ' ',
            'tight': token['tight'],
        }
        for item in token['children']:
            yield self._render_list_item(parent, item, state)

app = TableApp()
if __name__ == "__main__":
    if len(argv) > 1 and Path(argv[1]).exists():
        app.path = Path(argv[1])
    app.run()
