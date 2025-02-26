from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QFrame, QSplitter
from PyQt6.QtCore import Qt
from .mini_calendar import MiniCalendar
from .resource_monitor import ResourceMonitor
import os  # Añadir esta importación

class SidebarContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Crear un splitter vertical para permitir el resize
        self.splitter = QSplitter(Qt.Orientation.Vertical)

        # Contenedor superior para el selector y las vistas
        top_container = QWidget()
        top_layout = QVBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        # Construir la ruta correcta al archivo SVG
        arrow_down_icon = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'arrow_down.svg')

        # Selector de visualización
        self.view_selector = QComboBox()
        self.view_selector.addItem("Calendar View")
        self.view_selector.addItem("CPU and Memory Use")
        self.view_selector.currentIndexChanged.connect(self.change_view)
        self.view_selector.setStyleSheet(f"""
            QComboBox {{
                padding: 5px;
                border: 1px solid #dadce0;
                border-radius: 4px;
                background: white;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: url({arrow_down_icon.replace('\\', '/')});
                width: 12px;
                height: 12px;
            }}
        """)
        top_layout.addWidget(self.view_selector)

        # Mini Calendario
        self.mini_calendar = MiniCalendar()
        top_layout.addWidget(self.mini_calendar)

        # Monitor de recursos
        self.resource_monitor = ResourceMonitor()
        self.resource_monitor.setVisible(False)
        top_layout.addWidget(self.resource_monitor)

        # Agregar el contenedor superior al splitter
        self.splitter.addWidget(top_container)

        # Cuadrado negro en la parte inferior
        black_square = QFrame()
        black_square.setStyleSheet("background-color: black;")
        black_square.setMinimumHeight(300)  # Altura mínima
        self.splitter.addWidget(black_square)

        # Agregar el splitter al layout principal
        layout.addWidget(self.splitter)

    def change_view(self):
        """Cambia la vista según la selección del combo box"""
        if self.view_selector.currentText() == "Calendar View":
            self.mini_calendar.setVisible(True)
            self.resource_monitor.setVisible(False)
        else:
            self.mini_calendar.setVisible(False)
            self.resource_monitor.setVisible(True) 