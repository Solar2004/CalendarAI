from PyQt6.QtWidgets import QApplication
from .theme import get_dark_palette, get_light_palette
from config.constants import DARK_MODE_STYLE

class ThemeManager:
    def __init__(self):
        self._dark_mode = False

    @property
    def is_dark_mode(self):
        return self._dark_mode

    def toggle_theme(self):
        self._dark_mode = not self._dark_mode
        self._apply_theme()

    def _apply_theme(self):
        app = QApplication.instance()
        if self._dark_mode:
            app.setPalette(get_dark_palette())
            app.setStyleSheet(DARK_MODE_STYLE)
        else:
            app.setPalette(get_dark_palette())
            app.setStyleSheet("")

    def apply_current_theme(self):
        self._apply_theme() 