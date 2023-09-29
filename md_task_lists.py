import re

__all__ = ['md_task_lists']


TASK_LIST_ITEM = re.compile(r'^(\[[ xX]\])\s+')


def md_task_lists_hook(md, state):
    return _rewrite_all_list_items(state.tokens)


def md_render_task_list_item(renderer, text, checked=False):
    checkbox = ''
    if checked:
        checkbox += '[x] '
    else:
        checkbox += '[ ] '

        text = checkbox + text
    return text


def md_task_lists(md):
    md.before_render_hooks.append(md_task_lists_hook)
    if md.renderer and md.renderer.NAME == 'markdown':
        md.renderer.register('task_list_item', md_render_task_list_item)


def _rewrite_all_list_items(tokens):
    for tok in tokens:
        if tok['type'] == 'list_item':
            _rewrite_list_item(tok)
        if 'children' in tok:
            _rewrite_all_list_items(tok['children'])
    return tokens


def _rewrite_list_item(tok):
    children = tok['children']
    if children:
        first_child = children[0]
        text = first_child.get('text', '')
        m = TASK_LIST_ITEM.match(text)
        if m:
            mark = m.group(1)
            first_child['text'] = text[m.end():]

            tok['type'] = 'task_list_item'
            tok['attrs'] = {'checked': mark != '[ ]'}
