from itertools import cycle
from pathlib import Path
from sys import argv

from markdown_it import MarkdownIt
from rich.text import Text
from textual.app import App, ComposeResult
from textual.coordinate import Coordinate
from textual.reactive import var
from textual.widgets import DataTable

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
    md = MarkdownIt()
    tokens = None
    table = None
    complete_col_key = "complete"
    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        self.table = self.query_one(DataTable)
        self.table.cursor_type = "row"
        self.table.zebra_stripes = True
        self.add_title_columns()
        #self.table.add_rows(ROWS[1:])
        #todo: styled columns instead of rows. And instead of Text, we make our own Complete and TaskText types
        for row in ROWS[0:]:
            # Adding styled and justified `Text` objects instead of plain strings.
            styled_row = [
                Text(str(cell), style="#cccccc", justify="left") for cell in row
            ]
            self.table.add_row(*styled_row)
        self.set_table_from_file()

    def add_title_columns(self):
        self.table.add_column("X",width=3,key=self.complete_col_key)
        self.table.add_column(Text("Task",justify="center")) # centers the label 'task'.
    def set_table_from_file(self):
        with open(self.path, encoding="utf-8") as f:
            self.table.clear()
            data = f.read()
            self.tokens = self.md.parse(data)
            liopen = False
            for token in self.tokens:
                if token.type == 'list_item_open':
                    liopen = True
                    continue
                if token.type == 'list_item_close':
                    liopen = False
                    continue
                if liopen and token.type == 'inline':
                    completed = False
                    check = token.content[:3]
                    if check == "[ ]":
                        completed = False
                    if check == "[x]" or check == "[X]":
                        completed = True

                    styled_row = [
                        completed, Text(str(token.content[3:]), style="#cccccc", justify="left")
                    ]
                    self.table.add_row(*styled_row)

    #def save(self):
     #   with open(self.path, 'w',encoding="utf-8") as f:
      #      self.tokens

    def key_c(self):
        table = self.table
        table.move_cursor(row=table.cursor_row + 1, animate=False)

    def key_space(self):
        table = self.table
        row = self.selected_row()
        current = table.get_cell(row,self.complete_col_key)
        table.update_cell(row,self.complete_col_key,not current)
        # how do we connect this with the appropriate token?
        # keep a dictionary of tokens and rows right? just literally connect them together using the row?
    def key_d(self):
        table = self.table
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        table.remove_row(row_key)

    def selected_row(self):
        table = self.query_one(DataTable)
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        return row_key

app = TableApp()
if __name__ == "__main__":
    if len(argv) > 1 and Path(argv[1]).exists():
        app.path = Path(argv[1])
    app.run()
