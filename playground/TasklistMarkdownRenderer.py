from mistune.renderers.markdown import MarkdownRenderer
from mistune.util import strip_end
from typing import Dict, Any
from mistune import BlockState

class TaskListMarkdownRenderer(MarkdownRenderer):
    def render_token(self, token, state):
        func = self._get_method(token['type'])
        # hack workaround for register not working?
        if token['type'] == 'task_list_item':
            func = self.render_task_list_item

        return func(token, state)

    def render_task_list_item(self, token: Dict[str, Any], state: BlockState) -> str:
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
