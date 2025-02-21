from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import os

class SettingsPanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración del Calendario")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

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

        # Botón de cerrar
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

    def init_general_tab(self):
        layout = QVBoxLayout(self.general_tab)
        layout.addWidget(QLabel("Configuraciones generales del calendario aquí."))

    def init_appearance_tab(self):
        layout = QVBoxLayout(self.appearance_tab)
        layout.addWidget(QLabel("Configuraciones de apariencia del calendario aquí."))

    def init_notifications_tab(self):
        layout = QVBoxLayout(self.notifications_tab)
        layout.addWidget(QLabel("Configuraciones de notificaciones del calendario aquí.")) 