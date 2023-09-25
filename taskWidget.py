from dataclasses import dataclass
from threading import Thread
from time import sleep

from pytermgui import Container, StyleManager, real_length, tim


from pytermgui import MouseEvent, Widget


class Task(Widget):
    selected: bool = False
    label: str = "No action"

    def get_lines(self) -> list[str]:
        if self.selected:
            return [tim.parse("[inverse]"+self.label+"[/inverse]")]
        else:
            return [self.label]

    def on_left_click(self, event: MouseEvent) -> bool:
        self.label = "Left click"

        return True

    def on_click(self, event: MouseEvent) -> bool:
        self.label = "Generic click"

        return True

    def handle_mouse(self, event: MouseEvent) -> bool:
        # Make sure we call the super handler
        if super().handle_mouse(event):
            return True

        self.label = "No action"
        return True

    def highlight(self,sel: bool):
        self.selected=sel