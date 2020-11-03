import curses
from _curses import window
from math import floor, ceil
from typing import Optional, Union, Callable

from pp import a2z
from pp.abstract_view import AbstractView
from pp.config import page_text_from_id

_pad_top: int = 2
_border_top: int = 1
border_height: int = 4


def translate_tab_title(tab_name: str):
    if tab_name == 'IN_PLAY':
        return "In-Play"
    else:
        return tab_name


class TabView(AbstractView):
    def __init__(self, max_cols: int, parent_callback: Optional[Callable] = None):
        self._extent_cols = max_cols - a2z.extent_cols
        if self._extent_cols < 2:
            raise Exception('Window is too narrow')

        # noinspection PyTypeChecker
        self._border_wnd: window = curses.newwin(border_height, self._extent_cols, _border_top, a2z.extent_cols)
        self._is_focused = False

        self._longest_tab_name: int = 0
        self._tab_column_count: int = 0
        self._tab_row_count: int = 0
        self._tabs: list[dict[str, Union[str, int]]] = []
        self._tabs_pad: Optional[window] = None
        self._pad_first_line: int = 0
        self._pad_update_needed: bool = True
        self._current_selection: Optional[int] = None
        self._previous_selection: Optional[int] = None
        self.set_new_tab_list('', {}, [{'title': 'Loading...', 'id': 0, 'cards': []}])
        self._page_id = ''
        self._page_info = {}
        self._parent_callback = parent_callback

    def set_new_tab_list(self, page_id: str, page_info: dict[str, Union[str, int]],
                         tabs: list[dict[str, Union[str, int, list[int]]]], default_tab: Optional[int] = None):
        self._page_id = page_id
        self._page_info = page_info
        self._border_wnd.erase()
        self._redraw_border(self._is_focused, always=True)

        if self._tabs_pad is not None:
            self._tabs_pad = None
        if len(tabs) == 0:
            self._current_selection = None
            self._tabs = []
        else:
            self._pad_first_line = 0
            self._longest_tab_name = len(max(tabs, default=0, key=lambda k: len(k['title']))['title'])
            self._tab_column_count = floor((self._extent_cols - 4) / (self._longest_tab_name + 4))
            if self._tab_column_count == 0:
                raise Exception('Window too narrow')
            self._tab_row_count = ceil(len(tabs) / self._tab_column_count)
            self._tabs = [{
                **tab,
                'y_pos': self._y_from_index(i),
                'x_pos': self._x_from_index(i),
                'title': translate_tab_title(tab['title'])
            } for i, tab in enumerate(tabs)]
            self._current_selection = self._tab_index_from_id(default_tab)
            self._previous_selection = None
            # noinspection PyTypeChecker
            self._tabs_pad: window = curses.newpad(self._tab_row_count,
                                                   self._tab_column_count * (self._longest_tab_name + 4))
            self._write_tabs_into_pad()

    def _write_tabs_into_pad(self):
        self._tabs_pad.erase()
        for item in self._tabs:
            self._tabs_pad.addstr(item['y_pos'], item['x_pos'], item['title'])
        self._update_selection_chevron()
        self._pad_update_needed = True

    def _x_from_index(self, i: int) -> int:
        return (i % self._tab_column_count) * (self._longest_tab_name + 4) + 4

    def _y_from_index(self, i: int) -> int:
        return floor(i / self._tab_column_count)

    def _tab_index_from_id(self, tab_id: Optional[int]) -> Optional[int]:
        if tab_id is None:
            return None
        return next((i for i, tab in enumerate(self._tabs) if tab['id'] == tab_id), None)

    def full_render(self, max_rows: int, max_cols: int, is_focused: bool):
        self._border_wnd.erase()
        self._redraw_border(is_focused, always=True)
        self.update_render(max_rows, max_cols)

    def update_render(self, max_rows: int, max_cols: int):
        self._update_selection_chevron()
        if self._pad_update_needed:
            self._pad_update_needed = False
            self._tabs_pad.noutrefresh(self._pad_first_line, 0,
                                       _pad_top, a2z.extent_cols + 1,
                                       3, max_cols - 1)

    def on_change_focus(self, is_focused: bool):
        self._redraw_border(is_focused)

    def on_resize(self, max_rows: int, max_cols: int, is_focused: bool):
        self._extent_cols = self._extent_cols = max_cols - a2z.extent_cols

        self._longest_tab_name = len(max(self._tabs, default=0, key=lambda k: len(k['title']))['title'])
        self._tab_column_count = floor((self._extent_cols - 4) / (self._longest_tab_name + 4))
        if self._tab_column_count == 0:
            raise Exception('Window too narrow')
        self._tab_row_count = ceil(len(self._tabs) / self._tab_column_count)
        self._tabs = [{
            **tab,
            'y_pos': self._y_from_index(i),
            'x_pos': self._x_from_index(i),
            'title': translate_tab_title(tab['title'])
        } for i, tab in enumerate(self._tabs)]
        # noinspection PyTypeChecker
        self._tabs_pad: window = curses.newpad(self._tab_row_count,
                                               self._tab_column_count * (self._longest_tab_name + 4) + 1)
        self._write_tabs_into_pad()
        self._border_wnd.resize(border_height, self._extent_cols)
        self.full_render(max_rows, max_cols, is_focused)

    def _redraw_border(self, is_focused: bool, always: bool = False):
        if always or self._is_focused != is_focused:
            self._is_focused = is_focused
            if is_focused:
                self._draw_border(curses.color_pair(3))
            else:
                self._draw_border(curses.color_pair(2))
            self._border_wnd.noutrefresh()
            self._maybe_scroll()
            self._pad_update_needed = True

    def _update_selection_chevron(self):
        if self._current_selection is None:
            return

        if self._previous_selection is not None:
            previous = self._tabs[self._previous_selection]
            self._tabs_pad.addch(previous['y_pos'], previous['x_pos'] - 2, ' ')

        current = self._tabs[self._current_selection]
        self._previous_selection = self._current_selection
        self._tabs_pad.addch(current['y_pos'], current['x_pos'] - 2, '>')
        self._pad_update_needed = True

    def _draw_border(self, colour_pair: int):
        self._border_wnd.bkgd(' ', colour_pair)
        self._border_wnd.border()
        title = page_text_from_id[self._page_id] if self._page_id in page_text_from_id else ''
        self._border_wnd.addstr(0, 3, title, colour_pair)

    def process_keystroke(self, key: int):
        if key == curses.KEY_DOWN:
            new_selection = self._current_selection + self._tab_column_count
            if new_selection < len(self._tabs):
                self._current_selection = new_selection
            self._maybe_scroll()
        elif key == curses.KEY_UP:
            new_selection = self._current_selection - self._tab_column_count
            if new_selection >= 0:
                self._current_selection = new_selection
            self._maybe_scroll()
        elif key == curses.KEY_LEFT:
            if self._current_selection % self._tab_column_count != 0:
                self._current_selection = self._current_selection - 1
            self._maybe_scroll()
        elif key == curses.KEY_RIGHT:
            if self._current_selection % self._tab_column_count != (self._tab_column_count - 1) \
                    and self._current_selection != len(self._tabs) - 1:
                self._current_selection = self._current_selection + 1
            self._maybe_scroll()
        elif key == curses.KEY_ENTER or key == ord('\n') or key == ord(' '):
            if self._parent_callback is not None and self._current_selection is not None:
                self._parent_callback('LOAD_TAB', tab=self._tabs[self._current_selection]['id'],
                                      page_info=self._page_info)

    def _maybe_scroll(self):
        if self._current_selection is None:
            return

        y_pos = self._tabs[self._current_selection]['y_pos']
        inner_height = self._border_wnd.getmaxyx()[0] - _pad_top
        bottom_row = self._pad_first_line + inner_height - 1

        if y_pos < self._pad_first_line:
            self._pad_first_line = y_pos
            self._pad_update_needed = True
        elif y_pos > bottom_row:
            self._pad_first_line = y_pos - inner_height + 1
            self._pad_update_needed = True
