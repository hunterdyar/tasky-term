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

def create_task(list,completed,text):
    t = mdTask(list,text)
    t.text = text
    t.complete = completed
    t.parent = list
    return t

class MDList:
    # items is sorted
    items = []

    # quick reference, presumed unsorted
    categories = []
    path = ""

    def populate_from_file(self, path):
        self.items.clear()
        self.path = path
        with open(self.path, "a+", encoding="utf-8") as f:
            self.items.clear()
            f.seek(0)
            data = f.read().splitlines()
            for line in data:
                item = get_md_item_from_line(self, line.strip())
                # this could be a filter later? I want LINQ
                if item is mdHeader:
                    self.categories.append(item)
                self.items.append(item)
            return

    def get_tasks(self):
        x = list(filter(lambda x: isinstance(x,mdTask), self.items))
        return x

    def insert_task_after_item(self,prevItem,completed,task):
        index = self.items.index(prevItem)+1
        new_task = create_task(self,completed,task)
        self.items.insert(index,new_task)
        return new_task
    # todo: insert at end of category.
        # loop through items until category is full
        # x = i if i is task; until end of file or next category

    def remove_item(self, task):
        self.items.remove(task)

    def add_task(self, completed, text):
        # todo: replace with quicker iteration from end of list
        if len(self.items) == 0:
            new_task = create_task(self, completed, text)
            self.items.append(new_task)
            return new_task

        # default to adding at end of list
        last_task = self.items[-1]

        tasks = self.get_tasks()
        if len(tasks) != 0:
            last_task = tasks[-1]
        return self.insert_task_after_item(last_task, completed, text)


    def write_to_file(self, path):
        self.path = path
        with open(self.path, 'w', encoding="utf-8") as f:
            t = ""
            for line in self.items:
                t += line.renderLine() + "\n"
            f.write(t)
            f.close()
            return

class mdItem(object):
    # Compose
    source = ""
    parent = None

    def __init__(self, parent, source_line):
        self.source = source_line
        self.parent = parent

    def renderLine(self):
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
        if len(source_line) > 5:
            self.text = source_line[5:].strip()
            self.complete = source_line[3] != " "


    def renderLine(self):
        t = "- [x] " if self.complete else "- [ ] "
        return t+self.text

    @staticmethod
    def check_line(line):
        # todo: replace with regex
        return line[:3] == "- [" and line[4] == "]"


if __name__ == "__main__":
    mdlist = MDList()
    if len(sys.argv) == 1:
        path = "todo.md"
    else:
        path = sys.argv[1]
    mdlist.populate_from_file(path)
    mdlist.add_task(False, "Testing! A new todo! From the file!")
    mdlist.write_to_file(path)
