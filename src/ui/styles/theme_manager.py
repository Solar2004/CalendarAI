from PyQt6.QtWidgets import QApplication
from .theme import get_dark_palette, get_light_palette, Theme
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
        return self._dark_mode  # Return the new theme state

    def set_theme(self, is_dark_mode):
        """Set the theme to light or dark"""
        if self._dark_mode != is_dark_mode:
            self._dark_mode = is_dark_mode
            self._apply_theme()

    def _apply_theme(self):
        """Apply the current theme to the application"""
        app = QApplication.instance()
        
        # Set the theme in the Theme class
        Theme.set_theme(self._dark_mode)
        
        # Update all theme styles
        self._update_theme_styles()
        
        # Set the palette
        if self._dark_mode:
            app.setPalette(get_dark_palette())
        else:
            app.setPalette(get_light_palette())

    def _update_theme_styles(self):
        """Update all theme styles based on the current theme"""
        if self._dark_mode:
            # Set dark theme styles
            Theme.BUTTON_STYLE = Theme.BUTTON_STYLE_DARK
            Theme.MENUBAR_STYLE = Theme.MENUBAR_STYLE_DARK
            Theme.MAIN_WINDOW_STYLE = Theme.MAIN_WINDOW_STYLE_DARK
            Theme.CHAT_INPUT_STYLE = Theme.CHAT_INPUT_STYLE_DARK
            Theme.CHAT_MESSAGE_USER_STYLE = Theme.CHAT_MESSAGE_USER_STYLE_DARK
            Theme.CHAT_MESSAGE_AI_STYLE = Theme.CHAT_MESSAGE_AI_STYLE_DARK
            Theme.CHAT_CONTAINER_STYLE = Theme.CHAT_CONTAINER_STYLE_DARK
            Theme.CHAT_TIMESTAMP_STYLE = Theme.CHAT_TIMESTAMP_STYLE_DARK
            Theme.SIDEBAR_STYLE = Theme.SIDEBAR_STYLE_DARK
            Theme.SIDEBAR_BACKGROUND = Theme.SIDEBAR_BACKGROUND_DARK
            Theme.ICON_BUTTON_STYLE = Theme.ICON_BUTTON_STYLE_DARK
            Theme.SCROLLBAR_STYLE = Theme.SCROLLBAR_STYLE_DARK
            Theme.QUICK_ACTION_BUTTON_STYLE = Theme.QUICK_ACTION_BUTTON_STYLE_DARK
            Theme.AI_BUTTON_STYLE = Theme.AI_BUTTON_STYLE_DARK
        else:
            # Set light theme styles
            Theme.BUTTON_STYLE = Theme.BUTTON_STYLE_LIGHT
            Theme.MENUBAR_STYLE = Theme.MENUBAR_STYLE_LIGHT
            Theme.MAIN_WINDOW_STYLE = Theme.MAIN_WINDOW_STYLE_LIGHT
            Theme.CHAT_INPUT_STYLE = Theme.CHAT_INPUT_STYLE_LIGHT
            Theme.CHAT_MESSAGE_USER_STYLE = Theme.CHAT_MESSAGE_USER_STYLE_LIGHT
            Theme.CHAT_MESSAGE_AI_STYLE = Theme.CHAT_MESSAGE_AI_STYLE_LIGHT
            Theme.CHAT_CONTAINER_STYLE = Theme.CHAT_CONTAINER_STYLE_LIGHT
            Theme.CHAT_TIMESTAMP_STYLE = Theme.CHAT_TIMESTAMP_STYLE_LIGHT
            Theme.SIDEBAR_STYLE = Theme.SIDEBAR_STYLE_LIGHT
            Theme.SIDEBAR_BACKGROUND = Theme.SIDEBAR_BACKGROUND_LIGHT
            Theme.ICON_BUTTON_STYLE = Theme.ICON_BUTTON_STYLE_LIGHT
            Theme.SCROLLBAR_STYLE = Theme.SCROLLBAR_STYLE_LIGHT
            Theme.QUICK_ACTION_BUTTON_STYLE = Theme.QUICK_ACTION_BUTTON_STYLE_LIGHT
            Theme.AI_BUTTON_STYLE = Theme.AI_BUTTON_STYLE_LIGHT

    def apply_current_theme(self):
        """Apply the current theme"""
        self._apply_theme()
