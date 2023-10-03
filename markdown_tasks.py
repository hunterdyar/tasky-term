import sys

# CHECKBOX_PATTERN = "^\s*\(- \|\* \)\?\(\[[^\]]*\] \)\?."
def get_md_item_from_line(parent,line):
    # if it is a task, return task, etc.

    # don't bother with edge cases of regex and checks on empty strings.
    if line == "":
        return mdItem(parent, "")

    if mdTask.check_line(line):
        return mdTask(parent, line)

    if mdHeader.check_line(line):
        return mdHeader(parent, line)

    return mdItem(parent, line)

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
                #todo: get rid of .strip after regex so we can keep leading whitespace.
                self.items.append(get_md_item_from_line(self, line.strip()))

    def write_to_file(self, path):
        with open(self.path, 'w', encoding="utf-8") as f:
            t = ""
            for line in self.items:
                t += line.renderLine() + "\n"
            f.write(t)
            f.close()


class mdItem(object):
    # Compose
    source = ""
    parent = None

    def __init__(self, parent, source_line):
        self.source = source_line
        self.parent = parent

    def renderLine(self):
        print("render normal line: "+self.source)
        return self.source

    @staticmethod
    def check_line(line):
        return True

class mdHeader(mdItem):
    heading = 2
    def __init__(self, parent, source_line):
        self.source = source_line.strip()
        self.parent = parent
        heading = 1
        while source_line[heading-1] == "#" and heading < len(source_line)-1 and heading < 6:
            heading += 1
        self.text = source_line[heading:].strip()

    def renderLine(self):
        print("render heading "+str(self.heading))
        t = "#" * self.heading
        t += " "+self.text
        return t

    @staticmethod
    def check_line(line):
        return line[0] == "#"

class mdTask(mdItem):
    complete = False
    text = ""

    def __init__(self, parent, source_line):
        self.source = source_line.strip()
        self.parent = parent
        self.text = source_line[5:].strip()
        self.complete = source_line[3] != " "

    def renderLine(self):
        t = "- [x] " if self.complete else "- [ ] "
        print("render task: "+t+self.text)
        return t+self.text

    @staticmethod
    def check_line(line):
        # todo: replace with regex
        return line[:3] == "- [" and line[4] == "]"


if __name__ == "__main__":
    mdlist = MDList()
    if(len(sys.argv) == 1):
        path = "demo.md"
    else:
        path = sys.argv[1]
    mdlist.populate_from_file(path)
   # mdlist.items.append(md_item("An extra line!"))
    mdlist.write_to_file(path)
