import time
from taskWidget import Task

import pytermgui
import pytermgui as ptg
from pytermgui import Container

import mistletoe
from mistletoe import Document
from mistletoe.markdown_renderer import MarkdownRenderer

file = """
- [ ] unchecked task
- [x] checked task
- [ ] another task to do.
"""

# m = mistletoe.markdown(file)
doc = Document(file)

def macro_time(fmt: str) -> str:
    return time.strftime(fmt)

def macro_tasks(fmt: str) -> str:
    return MarkdownRenderer().render(doc)

ptg.tim.define("!time", macro_time)

ptg.tim.define("!tasks", macro_tasks)

container = ptg.Window()
container.set_title("Tasky")

tasks = []
for w in range(5):
    tasks.append(Task())
tasks[2].highlight(True)

container.set_widgets(tasks)

with ptg.WindowManager() as manager:
    manager.layout.add_slot("Body")
    manager.add(
        container
    )