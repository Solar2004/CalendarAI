from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QFrame, QSplitter
from PyQt6.QtCore import Qt
from .mini_calendar import MiniCalendar
from .resource_monitor import ResourceMonitor
from ..styles.theme import Theme
import os  # Añadir esta importación

class SidebarContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.content_widget = None
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Crear un splitter vertical para permitir el resize
        self.splitter = QSplitter(Qt.Orientation.Vertical)

        # Contenedor superior para el selector y las vistas
        top_container = QWidget()
        top_layout = QVBoxLayout(top_container)
        top_layout.setContentsMargins(10, 10, 10, 10)
        top_layout.setSpacing(10)

        # Construir la ruta correcta al archivo SVG
        arrow_down_icon = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'arrow_down.svg')

        # Selector de visualización
        self.view_selector = QComboBox()
        self.view_selector.addItem("Calendar View")
        self.view_selector.addItem("CPU and Memory Use")
        self.view_selector.currentIndexChanged.connect(self.change_view)
        
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

        # Contenedor para el contenido personalizado (chat_sidebar)
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # Agregar el contenedor de contenido al splitter
        self.splitter.addWidget(self.content_container)

        # Agregar el splitter al layout principal
        layout.addWidget(self.splitter)

    def apply_styles(self):
        """Aplica estilos basados en el tema actual"""
        is_dark = Theme.is_dark_mode
        bg_color = Theme.DARK_SIDEBAR_BG if is_dark else Theme.LIGHT_SIDEBAR_BG
        text_color = Theme.DARK_TEXT if is_dark else Theme.LIGHT_TEXT
        border_color = Theme.DARK_BORDER if is_dark else Theme.LIGHT_BORDER
        
        # Estilo para el contenedor
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                color: {text_color};
            }}
        """)
        
        # Estilo para el selector de vista
        self.view_selector.setStyleSheet(f"""
            QComboBox {{
                padding: 8px;
                border: 1px solid {border_color};
                border-radius: 4px;
                background: {bg_color};
                color: {text_color};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: url({os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'arrow_down.svg').replace('\\', '/')});
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                selection-background-color: {Theme.DARK_HOVER if is_dark else Theme.LIGHT_HOVER};
            }}
        """)
        
        # Estilo para el splitter
        self.splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {border_color};
                height: 1px;
            }}
        """)

    def set_content(self, widget):
        """Establece el widget de contenido en el contenedor"""
        # Limpiar el contenido anterior si existe
        if self.content_widget:
            self.content_layout.removeWidget(self.content_widget)
            self.content_widget.setParent(None)
        
        # Establecer el nuevo contenido
        self.content_widget = widget
        self.content_layout.addWidget(widget)
        
        # Ajustar tamaños del splitter (30% arriba, 70% abajo)
        total_height = self.height()
        self.splitter.setSizes([int(total_height * 0.3), int(total_height * 0.7)])

    def change_view(self):
        """Cambia la vista según la selección del combo box"""
        if self.view_selector.currentText() == "Calendar View":
            self.mini_calendar.setVisible(True)
            self.resource_monitor.setVisible(False)
        else:
            self.mini_calendar.setVisible(False)
            self.resource_monitor.setVisible(True)
            
    def update_theme(self):
        """Actualiza los estilos cuando cambia el tema"""
        self.apply_styles()
        
        # Actualizar componentes hijos si tienen método update_theme
        if hasattr(self.mini_calendar, 'update_theme'):
            self.mini_calendar.update_theme()
            
        if hasattr(self.resource_monitor, 'update_theme'):
            self.resource_monitor.update_theme()
            
        if self.content_widget and hasattr(self.content_widget, 'update_theme'):
            self.content_widget.update_theme() 