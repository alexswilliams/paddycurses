import curses
from _curses import window
from typing import Optional, Callable

from pp.abstract_view import AbstractView
from pp.config import all_sports, other_menu_items, page_id_from_text

longest_name_length = len(max(all_sports + other_menu_items, key=lambda k: len(k)))
default_menu_item = other_menu_items[0]
menu_items = [{'text': item, 'y_pos': i} for i, item in enumerate(other_menu_items)] \
             + [{'text': item, 'y_pos': i + len(other_menu_items) + 1} for i, item in enumerate(all_sports)]

_chevron_x: int = 2
_menu_item_text_x: int = 4
_pad_left: int = 2
_pad_width: int = longest_name_length + 4
_pad_top: int = 2
_pad_height: int = len(all_sports) + len(other_menu_items) + 1
_border_top: int = 1
extent_cols = _pad_width + 4


class A2ZView(AbstractView):
    def __init__(self, max_rows: int, parent_callback: Optional[Callable] = None):
        self._current_selection = next((i for i, x in enumerate(menu_items) if x['text'] == default_menu_item), 0)
        self._previous_selection = self._current_selection

        # noinspection PyTypeChecker
        self._menu_pad: window = curses.newpad(_pad_height, _pad_width)
        self._pad_first_line = 0
        self._pad_update_needed = True
        self._write_menu_into_pad()

        # noinspection PyTypeChecker
        self._border_wnd: window = curses.newwin(max_rows - 2, extent_cols, _border_top, 0)
        self._is_focused = False

        self._parent_callback = parent_callback

    def _write_menu_into_pad(self):
        self._menu_pad.erase()
        for item in menu_items:
            self._menu_pad.addstr(item['y_pos'], _menu_item_text_x, item['text'])

    def full_render(self, max_rows: int, max_cols: int, is_focused: bool):
        self._border_wnd.erase()
        self._redraw_border(is_focused, always=True)
        self.update_render(max_rows, max_cols)

    def update_render(self, max_rows: int, max_cols: int):
        self._update_selection_chevron()
        if self._pad_update_needed:
            self._pad_update_needed = False
            self._menu_pad.noutrefresh(self._pad_first_line, 0,
                                       _pad_top, _pad_left, max_rows - _pad_top - 1,
                                       _pad_width + _pad_left)

    def on_change_focus(self, is_focused: bool):
        self._redraw_border(is_focused)

    def on_resize(self, max_rows: int, max_cols: int, is_focused: bool):
        self._border_wnd.resize(max_rows - 2, extent_cols)
        self._pad_update_needed = True
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
        previous = menu_items[self._previous_selection]
        current = menu_items[self._current_selection]
        self._previous_selection = self._current_selection
        self._menu_pad.addch(previous['y_pos'], _chevron_x, ' ')
        self._menu_pad.addch(current['y_pos'], _chevron_x, '>')
        self._pad_update_needed = True

    def _draw_border(self, colour_pair: int):
        self._border_wnd.bkgd(' ', colour_pair)
        self._border_wnd.border()
        self._border_wnd.addstr(0, 3, "A-Z Sports", colour_pair)

    def process_keystroke(self, key: int):
        if key == curses.KEY_DOWN:
            self._current_selection = min(self._current_selection + 1, len(menu_items) - 1)
            self._maybe_scroll()
        elif key == curses.KEY_UP:
            self._current_selection = max(self._current_selection - 1, 0)
            self._maybe_scroll()
        elif key == curses.KEY_ENTER or key == ord('\n') or key == ord(' '):
            if self._parent_callback is not None:
                self._parent_callback('LOAD_PAGE', page=page_id_from_text[menu_items[self._current_selection]['text']])

    def _maybe_scroll(self):
        y_pos = menu_items[self._current_selection]['y_pos']
        inner_height = self._border_wnd.getmaxyx()[0] - _pad_top
        bottom_row = self._pad_first_line + inner_height - 1

        if y_pos < self._pad_first_line:
            self._pad_first_line = y_pos
            self._pad_update_needed = True
        elif y_pos > bottom_row:
            self._pad_first_line = y_pos - inner_height + 1
            self._pad_update_needed = True
