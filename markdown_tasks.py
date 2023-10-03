import sys

CHECKBOX_PATTERN = "^\s*\(- \|\* \)\?\(\[[^\]]*\] \)\?."
def get_md_item_from_line(parent,line):
    # if it is a task, return task, etc.
    return md_item(parent,line)

class MDList:
    items = []
    path = ""

    def populate_from_file(self, path):
        self.items.clear()
        self.path = path
        with open(self.path, encoding="utf-8") as f:
            self.items.clear()
            data = f.read().splitlines()
            for line in data:
                self.items.append(get_md_item_from_line(self,line))

    def write_to_file(self, path):
        with open(self.path, 'w', encoding="utf-8") as f:
            t = ""
            for line in self.items:
                t += line.renderLine() + "\n"
            f.write(t)
            f.close()


class md_item(object):
    # Compose
    source = ""
    parent = None

    def __init__(self, parent, source_line):
        self.source = source_line
        self.parent = parent

    def renderLine(self):
        return self.source


class Task(md_item):
    complete = False
    text = ""


if __name__ == "__main__":
    mdlist = MDList()
    path = sys.argv[1]
    mdlist.populate_from_file(path)
   # mdlist.items.append(md_item("An extra line!"))
    mdlist.write_to_file(path)
