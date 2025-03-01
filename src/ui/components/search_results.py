from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, 
    QLabel, QPushButton, QHBoxLayout,
    QGraphicsDropShadowEffect, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon, QColor
from models.event import Event
from datetime import datetime
import os
from ..styles.theme import Theme

class SearchResultItem(QWidget):
    clicked = pyqtSignal(list)  # Emite lista de eventos cuando se hace clic

    def __init__(self, title, description, count, events, parent=None):
        super().__init__(parent)
        self.events = events
        self.init_ui(title, description, count)

    def init_ui(self, title, description, count):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(0)

        # Contenedor clickeable
        clickable_container = QWidget()
        clickable_layout = QHBoxLayout(clickable_container)
        clickable_layout.setContentsMargins(0, 0, 0, 0)
        clickable_layout.setSpacing(16)

        # Icono del evento
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'event_icon.svg')
        icon_label.setPixmap(QIcon(icon_path).pixmap(24, 24))
        clickable_layout.addWidget(icon_label)

        # Contenedor para el texto
        text_container = QVBoxLayout()
        text_container.setSpacing(4)

        # Título y contador
        title_container = QHBoxLayout()
        title_container.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-weight: 500;
                font-size: 14px;
                color: {Theme.LIGHT_ACCENT};
            }}
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
            desc_label.setMaximumWidth(600)
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

        self.setFixedHeight(72)  # Aumentado para más espacio
        
        # Aplicar estilos basados en el tema actual
        is_dark = Theme.is_dark_mode
        bg_color = Theme.DARK_BG if is_dark else Theme.LIGHT_BG
        border_color = Theme.DARK_BORDER if is_dark else Theme.LIGHT_BORDER
        hover_color = Theme.DARK_HOVER if is_dark else Theme.LIGHT_HOVER
        
        self.setStyleSheet(f"""
            SearchResultItem {{
                background: {bg_color};
                border-bottom: 1px solid {border_color};
                margin: 0;
                padding: 0;
            }}
            SearchResultItem:hover {{
                background: {hover_color};
            }}
            SearchResultItem:last-child {{
                border-bottom: none;
            }}
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
        min_width = 600
        max_width = 1000
        
        # Ajustar el ancho dentro de los límites
        self.popup_width = max(min_width, min(desired_width, max_width))
        self.setFixedWidth(self.popup_width)
        self.setMaximumHeight(500)  # Aumentado para mostrar más resultados

    def init_ui(self):
        # Usar un único layout para todo el widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Contenedor principal con sombra
        self.container = QFrame()
        self.container.setObjectName("container")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Aplicar estilos basados en el tema actual
        is_dark = Theme.is_dark_mode
        bg_color = Theme.DARK_BG if is_dark else Theme.LIGHT_BG
        border_color = Theme.DARK_BORDER if is_dark else Theme.LIGHT_BORDER
        text_color = Theme.DARK_TEXT if is_dark else Theme.LIGHT_TEXT
        secondary_text = Theme.DARK_SECONDARY_TEXT if is_dark else Theme.LIGHT_SECONDARY_TEXT
        hover_color = Theme.DARK_HOVER if is_dark else Theme.LIGHT_HOVER
        accent_color = Theme.DARK_ACCENT if is_dark else Theme.LIGHT_ACCENT

        # Título de resultados mejorado
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(16, 16, 16, 16)
        
        search_icon = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'search_icon.svg')
        search_icon.setPixmap(QIcon(icon_path).pixmap(16, 16))
        title_layout.addWidget(search_icon)
        
        self.title_label = QLabel("Resultados de búsqueda")
        self.title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 15px;
                font-weight: 500;
                color: {text_color};
                background: transparent;
            }}
        """)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        
        title_container.setStyleSheet(f"""
            QWidget {{
                background: {hover_color};
                border-bottom: 1px solid {border_color};
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
        """)
        container_layout.addWidget(title_container)
        
        # Área scrolleable para resultados
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)  # Quitar borde
        scroll.setStyleSheet(Theme.SCROLLBAR_STYLE)
        
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setSpacing(0)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.results_container.setStyleSheet(f"""
            QWidget {{
                background: {bg_color};
            }}
        """)
        
        scroll.setWidget(self.results_container)
        container_layout.addWidget(scroll)
        
        # Pie de resultados
        footer = QWidget()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 12, 16, 12)
        
        self.count_label = QLabel("0 resultados")
        self.count_label.setStyleSheet(f"""
            QLabel {{
                color: {secondary_text};
                font-size: 12px;
            }}
        """)
        footer_layout.addWidget(self.count_label)
        footer_layout.addStretch()
        
        footer.setStyleSheet(f"""
            QWidget {{
                background: {bg_color};
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
                border-top: 1px solid {border_color};
            }}
        """)
        container_layout.addWidget(footer)
        
        # Aplicar sombra al contenedor principal
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        self.container.setGraphicsEffect(shadow)
        
        # Estilo del contenedor principal
        self.container.setStyleSheet(f"""
            QFrame#container {{
                background: {bg_color};
                border-radius: 8px;
                border: 1px solid {border_color};
            }}
        """)
        
        main_layout.addWidget(self.container)

    def show_under_widget(self, widget):
        """Muestra el popup debajo del widget especificado"""
        # Actualizar el ancho cada vez que se muestra
        main_window = self.window()
        window_width = main_window.width()
        desired_width = int(window_width * 0.7)
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
        for i in reversed(range(self.results_layout.count())):
            widget = self.results_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        if not results:
            # Mostrar mensaje de no resultados
            no_results = QLabel("No se encontraron resultados")
            no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_results.setStyleSheet(f"""
                QLabel {{
                    padding: 32px;
                    color: {Theme.DARK_SECONDARY_TEXT if Theme.is_dark_mode else Theme.LIGHT_SECONDARY_TEXT};
                    font-size: 14px;
                }}
            """)
            self.results_layout.addWidget(no_results)
            self.count_label.setText("0 resultados")
            return
        
        # Crear widgets para cada resultado
        total_events = 0
        for result in results:
            # Verificar si el resultado es un diccionario (formato nuevo) o un objeto Event (formato antiguo)
            if isinstance(result, dict):
                title = result['title']
                events = result['events']
                count = result['count']
                
                # Crear descripción
                if count == 1:
                    event = events[0]
                    description = f"{event.start_datetime.strftime('%d/%m/%Y %H:%M')} - {event.end_datetime.strftime('%H:%M')}"
                else:
                    # Mostrar rango de fechas para múltiples eventos
                    start_dates = [e.start_datetime for e in events]
                    end_dates = [e.end_datetime for e in events]
                    min_date = min(start_dates)
                    max_date = max(end_dates)
                    description = f"{min_date.strftime('%d/%m/%Y')} - {max_date.strftime('%d/%m/%Y')} ({count} eventos)"
                
                # Crear item de resultado
                result_item = SearchResultItem(title, description, count, events)
                result_item.clicked.connect(self.eventClicked)
                self.results_layout.addWidget(result_item)
                
                total_events += count
            else:
                # Mantener compatibilidad con el formato antiguo (objetos Event)
                # Agrupar resultados por título
                grouped_results = {}
                for event in results:
                    if event.title in grouped_results:
                        grouped_results[event.title].append(event)
                    else:
                        grouped_results[event.title] = [event]
                
                # Crear widgets para cada grupo
                for title, events in grouped_results.items():
                    # Crear descripción
                    if len(events) == 1:
                        event = events[0]
                        description = f"{event.start_datetime.strftime('%d/%m/%Y %H:%M')} - {event.end_datetime.strftime('%H:%M')}"
                    else:
                        # Mostrar rango de fechas para múltiples eventos
                        start_dates = [e.start_datetime for e in events]
                        end_dates = [e.end_datetime for e in events]
                        min_date = min(start_dates)
                        max_date = max(end_dates)
                        description = f"{min_date.strftime('%d/%m/%Y')} - {max_date.strftime('%d/%m/%Y')} ({len(events)} eventos)"
                    
                    # Crear item de resultado
                    result_item = SearchResultItem(title, description, len(events), events)
                    result_item.clicked.connect(self.eventClicked)
                    self.results_layout.addWidget(result_item)
                
                total_events = len(results)
                break  # Solo procesamos una vez si es el formato antiguo
        
        # Actualizar contador de resultados
        self.count_label.setText(f"{total_events} resultado{'s' if total_events != 1 else ''}")
        
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
                    
    def update_theme(self):
        """Actualiza los estilos cuando cambia el tema"""
        # Obtener colores del tema actual
        is_dark = Theme.is_dark_mode
        text_color = Theme.DARK_TEXT if is_dark else Theme.LIGHT_TEXT
        bg_color = Theme.DARK_BG if is_dark else Theme.LIGHT_BG
        border_color = Theme.DARK_BORDER if is_dark else Theme.LIGHT_BORDER
        hover_color = Theme.DARK_HOVER if is_dark else Theme.LIGHT_HOVER
        
        # Actualizar estilos del widget principal
        self.setStyleSheet(f"""
            QWidget#searchResultsWidget {{
                background: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
        """)
        
        # Actualizar título
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 15px;
                    font-weight: 500;
                    color: {text_color};
                    background: transparent;
                }}
            """)
            
        # Actualizar contenedor de título
        if hasattr(self, 'container'):
            container_layout = self.container.layout()
            title_container = None
            for i in range(container_layout.count()):
                widget = container_layout.itemAt(i).widget()
                if isinstance(widget, QWidget) and hasattr(self, 'title_label') and widget.findChildren(QLabel):
                    title_container = widget
                    break
                    
            if title_container:
                title_container.setStyleSheet(f"""
                    QWidget {{
                        background: {hover_color};
                        border-bottom: 1px solid {border_color};
                        border-top-left-radius: 8px;
                        border-top-right-radius: 8px;
                    }}
                """)
        
        # Actualizar contenedor de resultados
        if hasattr(self, 'results_container'):
            self.results_container.setStyleSheet(f"""
                QWidget {{
                    background: {bg_color};
                }}
            """)
            
        # Actualizar cada item de resultado
        if hasattr(self, 'results_layout'):
            for i in range(self.results_layout.count()):
                item = self.results_layout.itemAt(i).widget()
                if isinstance(item, SearchResultItem):
                    item.setStyleSheet(f"""
                        SearchResultItem {{
                            background: {bg_color};
                            border-bottom: 1px solid {border_color};
                            margin: 0;
                            padding: 0;
                        }}
                        SearchResultItem:hover {{
                            background: {hover_color};
                        }}
                        SearchResultItem:last-child {{
                            border-bottom: none;
                        }}
                    """)
        
        # Actualizar scrollbar
        for scroll in self.findChildren(QScrollArea):
            scroll.setStyleSheet(Theme.SCROLLBAR_STYLE) 