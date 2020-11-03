from abc import ABCMeta, abstractmethod


class AbstractView(metaclass=ABCMeta):
    @abstractmethod
    def full_render(self, max_rows: int, max_cols: int, is_focused: bool):
        pass

    @abstractmethod
    def update_render(self, max_rows: int, max_cols: int):
        pass

    @abstractmethod
    def on_change_focus(self, is_focused: bool):
        pass

    @abstractmethod
    def on_resize(self, max_rows: int, max_cols: int, is_focused: bool):
        pass

    @abstractmethod
    def process_keystroke(self, key: int):
        pass
