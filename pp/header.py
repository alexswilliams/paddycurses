import curses
from _curses import window

from pp.abstract_view import AbstractView

_title = 'PaddyCurses'
_login_btn = 'Login [^L]'


class HeaderView(AbstractView):
    def __init__(self, max_cols: int):
        # noinspection PyTypeChecker
        self._header_wnd: window = curses.newwin(1, max_cols, 0, 0)
        self.update_needed = True

    def full_render(self, max_rows: int, max_cols: int, is_focused: bool):
        self.update_render(max_rows, max_cols)

    def update_render(self, max_rows: int, max_cols: int):
        if self.update_needed:
            self.update_needed = False
            self._header_wnd.bkgd(' ', curses.color_pair(1))
            self._header_wnd.addstr(0, round(max_cols / 2 - len(_title) / 2), _title, curses.A_BOLD)
            self._header_wnd.addstr(0, max_cols - len(_login_btn) - 2, _login_btn)
            self._header_wnd.noutrefresh()

    def on_change_focus(self, is_focused: bool):
        pass

    def on_resize(self, max_rows: int, max_cols: int, is_focused: bool):
        self._header_wnd.resize(1, max_cols)
        self._header_wnd.erase()
        self.update_needed = True

    def process_keystroke(self, key: int):
        pass
