from dataclasses import dataclass
from threading import Thread
from time import sleep

from pytermgui import Container, StyleManager, real_length, tim
from pytermgui import MouseEvent, Widget


class Task(Widget):
    selected: bool = False
    completed: bool = False
    task: str = "Some Task"
    val: str = tim.parse("[inverse]" + "[ ]" + task + "[/inverse]")

    def refresh_macro_output(self):
        completedStr = "[x]" if self.completed else "[ ]"
        if self.selected:
            self.val = "[inverse]" + completedStr + " " + self.task + "[/inverse]"
        else:
            self.val = completedStr + " " + self.task
    def get_lines(self) -> list[str]:
        #self.refresh_macro_output()
        completedStr = "[x]" if self.completed else "[ ]"
        if self.selected:
            self.val = "[inverse]" + completedStr + " " + self.task + "[/inverse]"
        else:
            self.val = completedStr + " " + self.task
        return [tim.parse(self.val)]

    def on_left_click(self, event: MouseEvent) -> bool:
        self.toggle()
        self.refresh_macro_output()
        return True

    def handle_key(self, key: str) -> bool:
        return True

    def highlight(self,sel: bool):
        self.selected=sel
        self.refresh_macro_output()

    def toggle(self):
        self.completed = not self.completed
        self.refresh_macro_output()
