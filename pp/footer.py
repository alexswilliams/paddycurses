import curses
from _curses import window

from pp.abstract_view import AbstractView

_shortcuts = '[TAB] Change Focus    [q] Quit'
_bet_slip = 'Bet Slip: 0 Bets (£0.00)'


class FooterView(AbstractView):
    def __init__(self, max_rows, max_cols: int):
        # noinspection PyTypeChecker
        self._footer_wnd: window = curses.newwin(1, max_cols, max_rows - 1, 0)
        self.update_needed = True

    def full_render(self, max_rows: int, max_cols: int, is_focused: bool):
        self.update_render(max_rows, max_cols)

    def update_render(self, max_rows: int, max_cols: int):
        if self.update_needed:
            self.update_needed = False
            self._footer_wnd.bkgd(' ', curses.color_pair(1))
            self._footer_wnd.addstr(0, 1, _shortcuts)
            self._footer_wnd.noutrefresh()

    def on_change_focus(self, is_focused: bool):
        pass

    def on_resize(self, max_rows: int, max_cols: int, is_focused: bool):
        self._footer_wnd.resize(1, max_cols)
        self._footer_wnd.mvwin(max_rows - 1, 0)
        self.update_needed = True

    def process_keystroke(self, key: int):
        pass
