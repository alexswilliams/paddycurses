import curses
from _curses import window
from typing import Optional, Callable

from pp import a2z, tabs
from pp.abstract_view import AbstractView


class ContentView(AbstractView):
    def __init__(self, max_rows: int, max_cols: int, parent_callback: Optional[Callable] = None):
        self._current_selection = None
        self._previous_selection = self._current_selection

        self._border_left = a2z.extent_cols + 1
        self._border_top = tabs.border_height + 1
        self._border_width = max_cols - self._border_left - 1
        self._border_height = max_rows - self._border_top - 1

        # noinspection PyTypeChecker
        self._menu_pad: window = curses.newpad(1000, 1000)
        self._pad_first_line = 0
        self._pad_update_needed = True
        # populate pad

        # noinspection PyTypeChecker
        self._border_wnd: window = curses.newwin(self._border_height, self._border_width,
                                                 self._border_top, self._border_left)
        self._is_focused = False
        self._tab = None
        self._page_info = None
        self._parent_callback = parent_callback

    def full_render(self, max_rows: int, max_cols: int, is_focused: bool):
        self._border_wnd.erase()
        self._redraw_border(is_focused, always=True)
        self.update_render(max_rows, max_cols)

    def update_render(self, max_rows: int, max_cols: int):
        # self._update_selection_chevron()
        if self._pad_update_needed:
            self._pad_update_needed = False
            self._menu_pad.noutrefresh(self._pad_first_line, 0,
                                       self._border_top + 1, self._border_left + 1,
                                       self._border_height, self._border_width)

    def _draw_border(self, colour_pair: int):
        self._border_wnd.bkgd(' ', colour_pair)
        self._border_wnd.border()
        self._border_wnd.addstr(0, 3, "Cards & Coupons", colour_pair)

    def _redraw_border(self, is_focused: bool, always: bool = False):
        if always or self._is_focused != is_focused:
            self._is_focused = is_focused
            if is_focused:
                self._draw_border(curses.color_pair(3))
            else:
                self._draw_border(curses.color_pair(2))
            self._border_wnd.noutrefresh()
            # self._maybe_scroll()
            self._pad_update_needed = True

    def on_change_focus(self, is_focused: bool):
        self._redraw_border(is_focused)

    def on_resize(self, max_rows: int, max_cols: int, is_focused: bool):
        self._border_width = max_cols - self._border_left - 1
        self._border_height = max_rows - self._border_top - 1
        self._border_wnd.resize(self._border_height, self._border_width)
        self._pad_update_needed = True
        self.full_render(max_rows, max_cols, is_focused)

    def process_keystroke(self, key: int):
        pass

    def load_new_tab(self, tab, page_info):
        self._page_info = page_info
        self._tab = tab
        self._menu_pad.erase()

        items = []
        for card in tab['cards']:
            items.append("  " + card['title'])
            coupon_ids = [coupon['id'] for coupon in card['coupons']]
            for coupon_id in coupon_ids:
                coupon = tab['coupons'][coupon_id]
                if 'title' in coupon:
                    items.append("    " + coupon['title'])
                else:
                    items.append("    " + coupon['type'] + " for event " + str(coupon['eventId']))

        for i, item in enumerate(items):
            self._menu_pad.addstr(i, 0, item)
        self._pad_update_needed = True
