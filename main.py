import curses
import functools
import inspect
from _curses import window
from typing import Callable, Any, cast, Union, Optional

from pp.a2z import A2ZView
from pp.abstract_view import AbstractView
from pp.footer import FooterView
from pp.header import HeaderView
from pp.content import ContentView
from pp.rest import page_layout
from pp.tabs import TabView


def main_page(scr: window):
    curses.curs_set(0)
    scr.noutrefresh()
    callbacks = {}

    def command_callback(command: str, **kwargs: Any):
        if command in callbacks:
            callbacks[command](**kwargs)

    setup_colours()
    max_rows, max_cols = scr.getmaxyx()
    views: dict[str, AbstractView] = {
        'header': HeaderView(max_cols),
        'footer': FooterView(max_rows, max_cols),
        'a2z': A2ZView(max_rows, command_callback),
        'tabs': TabView(max_cols, command_callback),
        'content': ContentView(max_rows, max_cols, command_callback)
    }
    keypress_table: dict[str, Callable[[int], None]] = {name: view.process_keystroke for name, view in views.items()}
    focus: list[str] = ['a2z']
    dispatch_to: list[Callable[[int], None]] = [keypress_table[focus[0]]]

    full_render_current_state(scr, views, focus[0])
    curses.doupdate()

    callbacks = setup_callbacks(views, focus, dispatch_to)
    command_callback('LOAD_PAGE', page='HOMEPAGE')

    keep_going = True
    while keep_going:
        update_render_current_state(scr, views)
        curses.doupdate()

        key: int = scr.getch()
        if key == ord('q'):
            keep_going = False
        elif key == ord('\t'):
            focus[0] = next_focus(focus[0])
            update_focuses(views, focus[0])
            dispatch_to[0] = keypress_table[focus[0]]
        elif key == curses.KEY_RESIZE:
            curses.resizeterm(*scr.getmaxyx())
            scr.erase()
            scr.noutrefresh()
            resize_all(focus[0], views, scr)
        else:
            dispatch_to[0](key)


def setup_colours():
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)


def setup_callbacks(views: dict[str, AbstractView],
                    focus: list[str],
                    dispatch_to: list[Callable[[int], None]]) -> dict[str, functools.partial[None]]:
    def close_over(function: Callable[[Any], None]) -> functools.partial[None]:
        sig = inspect.signature(function)
        result = function
        if 'views' in sig.parameters:
            result = functools.partial(result, views=views)
        if 'focus' in sig.parameters:
            result = functools.partial(result, focus=focus)
        if 'dispatch_to' in sig.parameters:
            result = functools.partial(result, dispatch_to=dispatch_to)
        return result

    return {
        'LOAD_PAGE': close_over(load_page),
        'LOAD_TAB': close_over(load_tab)
    }


def full_render_current_state(scr: window, views: dict[str, AbstractView], focus: str):
    for name, view in views.items():
        view.full_render(*scr.getmaxyx(), focus == name)


def update_render_current_state(scr: window, views: dict[str, AbstractView]):
    for view in views.values():
        view.update_render(*scr.getmaxyx())


def resize_all(focus: str,
               views: dict[str, AbstractView],
               scr: window):
    for name, view in views.items():
        view.on_resize(*scr.getmaxyx(), focus == name)


def next_focus(focus: str) -> str:
    if focus == 'a2z':
        return 'tabs'
    if focus == 'tabs':
        return 'content'
    if focus == 'content':
        return 'a2z'


def update_focuses(views: dict[str, AbstractView],
                   focus: str):
    for name, view in views.items():
        view.on_change_focus(focus == name)


def load_page(page: str,
              views: dict[str, AbstractView]):
    page_data = page_layout.load_page(page)
    cast(TabView, views['tabs']).set_new_tab_list(page_id=page, page_info=page_data.page_info,
                                                  tabs=page_data.tabs, default_tab=page_data.default_tab)

    default_tab = next((tab for tab in page_data.tabs if tab['id'] == page_data.default_tab), None)
    load_tab(views=views, tab=default_tab, page_info=page_data.page_info)


def load_tab(views: dict[str, AbstractView],
             tab: Optional[dict[str, Union[str, int, list[int]]]],
             page_info: dict[str, Union[str, int]]):
    if 'content' in views.keys():
        cast(ContentView, views['content']).load_new_tab(tab, page_info)


if __name__ == "__main__":
    try:
        curses.wrapper(main_page)
    except KeyboardInterrupt:
        pass
