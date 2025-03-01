from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import os
from ..styles.theme import Theme
import logging

logger = logging.getLogger(__name__)

class SettingsPanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración del Calendario")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Crear el widget de pestañas
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(False)

        # Agregar pestañas
        self.general_tab = QWidget()
        self.appearance_tab = QWidget()
        self.notifications_tab = QWidget()

        self.tabs.addTab(self.general_tab, QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'settings_icon.svg')), "General")
        self.tabs.addTab(self.appearance_tab, QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'appearance_icon.svg')), "Apariencia")
        self.tabs.addTab(self.notifications_tab, QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'notifications_icon.svg')), "Notificaciones")

        # Configurar el contenido de las pestañas
        self.init_general_tab()
        self.init_appearance_tab()
        self.init_notifications_tab()

        layout.addWidget(self.tabs)

    def init_general_tab(self):
        layout = QVBoxLayout(self.general_tab)
        self.general_label = QLabel("Configuraciones generales del calendario aquí.")
        layout.addWidget(self.general_label)

    def init_appearance_tab(self):
        layout = QVBoxLayout(self.appearance_tab)
        self.appearance_label = QLabel("Configuraciones de apariencia del calendario aquí.")
        layout.addWidget(self.appearance_label)

    def init_notifications_tab(self):
        layout = QVBoxLayout(self.notifications_tab)
        self.notifications_label = QLabel("Configuraciones de notificaciones del calendario aquí.")
        layout.addWidget(self.notifications_label)
        
    def apply_theme(self):
        """Aplica estilos basados en el tema actual"""
        is_dark = Theme.is_dark_mode
        bg_color = Theme.DARK_BG if is_dark else Theme.LIGHT_BG
        text_color = Theme.DARK_TEXT if is_dark else Theme.LIGHT_TEXT
        border_color = Theme.DARK_BORDER if is_dark else Theme.LIGHT_BORDER
        secondary_text = Theme.DARK_SECONDARY_TEXT if is_dark else Theme.LIGHT_SECONDARY_TEXT
        
        # Estilo para el diálogo
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                color: {text_color};
            }}
            QTabWidget::pane {{
                border: 1px solid {border_color};
                border-radius: 4px;
                background-color: {bg_color};
            }}
            QTabBar::tab {{
                background-color: {Theme.DARK_HOVER if is_dark else "#f0f0f0"};
                border: 1px solid {border_color};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                color: {text_color};
            }}
            QTabBar::tab:selected {{
                background-color: {bg_color};
                border-bottom-color: {bg_color};
            }}
            QLabel {{
                color: {text_color};
            }}
        """)
        
        # Actualizar etiquetas
        if hasattr(self, 'general_label'):
            self.general_label.setStyleSheet(f"color: {text_color};")
            
        if hasattr(self, 'appearance_label'):
            self.appearance_label.setStyleSheet(f"color: {text_color};")
            
        if hasattr(self, 'notifications_label'):
            self.notifications_label.setStyleSheet(f"color: {text_color};")
            
    def update_theme(self):
        """Actualiza los estilos cuando cambia el tema"""
        self.apply_theme() 