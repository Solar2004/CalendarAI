from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, 
    QLabel, QPushButton, QHBoxLayout,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon, QColor
from models.event import Event
from datetime import datetime
import os

class SearchResultItem(QWidget):
    clicked = pyqtSignal(list)  # Emite lista de eventos cuando se hace clic

    def __init__(self, title, description, count, events, parent=None):
        super().__init__(parent)
        self.events = events
        self.init_ui(title, description, count)

    def init_ui(self, title, description, count):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        # Contenedor clickeable
        clickable_container = QWidget()
        clickable_layout = QHBoxLayout(clickable_container)
        clickable_layout.setContentsMargins(0, 0, 0, 0)
        clickable_layout.setSpacing(10)

        # Icono del evento
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'event_icon.svg')
        icon_label.setPixmap(QIcon(icon_path).pixmap(24, 24))
        clickable_layout.addWidget(icon_label)

        # Contenedor para el texto
        text_container = QVBoxLayout()
        text_container.setSpacing(2)

        # Título y contador
        title_container = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-weight: 500;
                font-size: 14px;
                color: #1a73e8;
            }
        """)
        title_container.addWidget(title_label)
        
        if count > 1:
            count_label = QLabel(f"({count})")
            count_label.setStyleSheet("color: #666; margin-left: 5px;")
            title_container.addWidget(count_label)
        
        title_container.addStretch()
        text_container.addLayout(title_container)

        # Información del evento
        if self.events:
            event = self.events[0]
            date_text = f"{event.start_datetime.strftime('%d/%m/%Y %H:%M')} - {event.end_datetime.strftime('%H:%M')}"
            date_label = QLabel(date_text)
            date_label.setStyleSheet("""
                QLabel {
                    color: #5f6368;
                    font-size: 12px;
                    margin-top: 2px;
                }
            """)
            text_container.addWidget(date_label)

        # Descripción (limitada a una línea)
        if description:
            desc_label = QLabel(description)
            # Usar un ancho fijo inicial, se ajustará después
            desc_label.setMaximumWidth(600)  # Ancho inicial conservador
            desc_label.setStyleSheet("""
                QLabel {
                    color: #5f6368;
                    font-size: 13px;
                    margin-top: 2px;
                    line-height: 1.4;
                }
            """)
            
            # Guardar referencia para ajustar después
            self.desc_label = desc_label
            self.description = description
            text_container.addWidget(desc_label)

        clickable_layout.addLayout(text_container)
        
        # Icono de flecha
        arrow_label = QLabel()
        arrow_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'arrow_right.svg')
        arrow_label.setPixmap(QIcon(arrow_path).pixmap(16, 16))
        clickable_layout.addWidget(arrow_label)

        layout.addWidget(clickable_container)

        # Establecer el cursor solo para el contenedor clickeable
        clickable_container.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCursor(Qt.CursorShape.ArrowCursor)  # Cursor normal para el resto

        self.setFixedHeight(65)
        self.setStyleSheet("""
            SearchResultItem {
                background: white;
                border-bottom: 1px solid #e8eaed;
                margin: 0;
                padding: 0;
            }
            SearchResultItem:hover {
                background: #f8f9fa;
            }
            SearchResultItem:last-child {
                border-bottom: none;
            }
        """)

        # Guardar referencia al contenedor clickeable
        self.clickable_container = clickable_container

    def resizeEvent(self, event):
        """Se llama cuando el widget cambia de tamaño"""
        super().resizeEvent(event)
        if hasattr(self, 'desc_label') and hasattr(self, 'description'):
            # Ajustar el ancho de la descripción al nuevo tamaño
            max_desc_width = int(self.width() * 0.8)
            self.desc_label.setMaximumWidth(max_desc_width)
            metrics = self.desc_label.fontMetrics()
            text = metrics.elidedText(self.description, Qt.TextElideMode.ElideRight, max_desc_width)
            self.desc_label.setText(text)

    def mousePressEvent(self, event):
        # Solo procesar el clic si está en el área clickeable
        if self.clickable_container.geometry().contains(event.pos()):
            from .event_details_dialog import EventDetailsDialog
            dialog = EventDetailsDialog(self.events, self.window())
            dialog.exec()
            self.clicked.emit(self.events)

class SearchResultsWidget(QWidget):
    eventClicked = pyqtSignal(list)  # Emite lista de eventos cuando se hace clic

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Obtener el ancho de la ventana principal
        main_window = self.window()
        window_width = main_window.width()
        
        # Calcular el 70% del ancho de la ventana
        desired_width = int(window_width * 0.7)
        
        # Establecer límites mínimo y máximo
        min_width = 600  # Aumentado de 500 a 600
        max_width = 1000  # Aumentado de 800 a 1000
        
        # Ajustar el ancho dentro de los límites
        self.popup_width = max(min_width, min(desired_width, max_width))
        self.setFixedWidth(self.popup_width)
        self.setMaximumHeight(400)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Contenedor principal con sombra
        self.container = QWidget()
        self.container.setObjectName("container")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Título de resultados mejorado
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(16, 12, 16, 12)
        
        search_icon = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'search_icon.svg')
        search_icon.setPixmap(QIcon(icon_path).pixmap(16, 16))
        title_layout.addWidget(search_icon)
        
        self.title_label = QLabel("Resultados de búsqueda")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 500;
                color: #202124;
                background: transparent;
            }
        """)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        
        title_container.setStyleSheet("""
            QWidget {
                background: #f8f9fa;
                border-bottom: 1px solid #dadce0;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """)
        container_layout.addWidget(title_container)

        # Área scrolleable para resultados
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: white;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f3f4;
                width: 8px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #dadce0;
                min-height: 40px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setSpacing(0)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(self.results_container)
        container_layout.addWidget(scroll)

        layout.addWidget(self.container)

        # Actualizar el estilo para una sombra más sutil
        self.setStyleSheet("""
            #container {
                background: white;
                border: 1px solid #dadce0;
                border-radius: 8px;
                margin: 8px;
            }
            QWidget {
                border-radius: 8px;
            }
        """)
        
        # Efecto de sombra más sutil
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.container.setGraphicsEffect(shadow)
        
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.container.setCursor(Qt.CursorShape.ArrowCursor)

    def show_under_widget(self, widget):
        """Muestra el popup debajo del widget especificado"""
        # Actualizar el ancho cada vez que se muestra
        main_window = self.window()
        window_width = main_window.width()
        desired_width = int(window_width * 0.7)  # Actualizado aquí también
        self.popup_width = max(600, min(desired_width, 1000))
        self.setFixedWidth(self.popup_width)
        
        pos = widget.mapToGlobal(QPoint(0, widget.height()))
        # Centrar horizontalmente con el widget de búsqueda
        pos.setX(pos.x() + (widget.width() - self.width()) // 2)
        pos.setY(pos.y() + 8)
        self.move(pos)
        self.show()

    def update_results(self, results):
        # Limpiar resultados anteriores
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not results:
            no_results = QLabel("No se encontraron resultados")
            no_results.setStyleSheet("""
                color: #5f6368;
                padding: 16px;
                font-size: 13px;
                background: white;
            """)
            no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_layout.addWidget(no_results)
        else:
            # Asegurarnos de que el contenedor tenga el ancho correcto
            self.results_container.setFixedWidth(self.width())
            
            for result in results:
                item = SearchResultItem(
                    result['title'],
                    result['description'],
                    result['count'],
                    result['events']
                )
                item.setFixedWidth(self.width())
                item.clicked.connect(lambda events: self.eventClicked.emit(events))
                self.results_layout.addWidget(item)

        self.show()

    def resizeEvent(self, event):
        """Se llama cuando el widget cambia de tamaño"""
        super().resizeEvent(event)
        # Actualizar el ancho de todos los items
        if hasattr(self, 'results_layout'):
            for i in range(self.results_layout.count()):
                item = self.results_layout.itemAt(i).widget()
                if isinstance(item, SearchResultItem):
                    item.setFixedWidth(self.width()) 