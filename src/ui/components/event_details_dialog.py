from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QWidget,
    QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import os
from datetime import datetime
from ..styles.theme import Theme
import logging

logger = logging.getLogger(__name__)

class EventDetailsDialog(QDialog):
    def __init__(self, events, parent=None):
        super().__init__(parent)
        self.events = events
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)  # Remove close button
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        self.setWindowTitle("Detalles del Evento")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Contenedor principal con scroll
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        content_widget = QWidget()
        self.content_widget = content_widget  # Store reference for theme updates
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)

        # Título del evento
        title_container = QHBoxLayout()
        
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'event_icon.svg')
        icon_label.setPixmap(QIcon(icon_path).pixmap(24, 24))
        title_container.addWidget(icon_label)

        title_label = QLabel(self.events[0].title)
        self.title_label = title_label
        title_container.addWidget(title_label)
        title_container.addStretch()
        
        # Si hay múltiples eventos, mostrar contador
        if len(self.events) > 1:
            count_label = QLabel(f"(Se repite {len(self.events)} veces)")
            self.count_label = count_label
            title_container.addWidget(count_label)
        
        content_layout.addLayout(title_container)

        # Fechas de los eventos con scroll si son muchas
        dates_widget = QWidget()
        dates_layout = QVBoxLayout(dates_widget)
        dates_layout.setSpacing(5)
        
        dates_label = QLabel("Fechas de ejecución:")
        self.dates_label = dates_label
        
        dates_scroll = QScrollArea()
        dates_scroll.setWidgetResizable(True)
        dates_scroll.setMaximumHeight(150)  # Altura máxima
        self.dates_scroll = dates_scroll
        
        dates_container = QWidget()
        dates_container_layout = QVBoxLayout(dates_container)
        
        self.date_labels = []
        for event in self.events:
            date_text = f"• {event.start_datetime.strftime('%d/%m/%Y %H:%M')} - {event.end_datetime.strftime('%H:%M')}"
            date_label = QLabel(date_text)
            self.date_labels.append(date_label)
            dates_container_layout.addWidget(date_label)
        
        dates_scroll.setWidget(dates_container)
        dates_layout.addWidget(dates_label)
        dates_layout.addWidget(dates_scroll)
        content_layout.addWidget(dates_widget)

        # ID del evento
        id_label = QLabel(f"ID: {self.events[0].google_event_id or 'No disponible'}")
        self.id_label = id_label
        content_layout.addWidget(id_label)

        # Color ID
        if hasattr(self.events[0], 'colorId'):
            color_label = QLabel(f"Color ID: {self.events[0].colorId}")
            self.color_label = color_label
            content_layout.addWidget(color_label)

        # Tags
        if hasattr(self.events[0], 'tags') and self.events[0].tags:
            tags_container = QHBoxLayout()
            tags_label = QLabel("Tags:")
            self.tags_label = tags_label
            tags_container.addWidget(tags_label)
            
            self.tag_labels = []
            for tag in self.events[0].tags:
                tag_label = QLabel(tag)
                self.tag_labels.append(tag_label)
                tags_container.addWidget(tag_label)
            tags_container.addStretch()
            content_layout.addLayout(tags_container)

        # Descripción con formato HTML
        if self.events[0].description:
            desc_label = QLabel("Descripción:")
            self.desc_title_label = desc_label
            content_layout.addWidget(desc_label)
            
            desc_text = QTextEdit()
            desc_text.setHtml(self.events[0].description)
            desc_text.setReadOnly(True)
            desc_text.setMinimumHeight(100)
            desc_text.setMaximumHeight(200)
            self.desc_text = desc_text
            content_layout.addWidget(desc_text)

        # JSON Raw Data
        raw_label = QLabel("Datos JSON:")
        self.raw_label = raw_label
        content_layout.addWidget(raw_label)
        
        raw_text = QTextEdit()
        raw_text.setPlainText(str(self.events[0].__dict__))
        raw_text.setReadOnly(True)
        raw_text.setMinimumHeight(100)
        raw_text.setMaximumHeight(200)
        self.raw_text = raw_text
        content_layout.addWidget(raw_text)

        self.scroll.setWidget(content_widget)
        layout.addWidget(self.scroll)

    def apply_theme(self):
        """Aplica estilos basados en el tema actual"""
        is_dark = Theme.is_dark_mode
        bg_color = Theme.DARK_BG if is_dark else Theme.LIGHT_BG
        text_color = Theme.DARK_TEXT if is_dark else Theme.LIGHT_TEXT
        secondary_text = Theme.DARK_SECONDARY_TEXT if is_dark else Theme.LIGHT_SECONDARY_TEXT
        border_color = Theme.DARK_BORDER if is_dark else Theme.LIGHT_BORDER
        accent_color = Theme.DARK_ACCENT if is_dark else Theme.LIGHT_ACCENT
        hover_color = Theme.DARK_HOVER if is_dark else Theme.LIGHT_HOVER
        
        # Estilo para el diálogo
        self.setStyleSheet(f"""
            QDialog {{
                background: {bg_color};
                color: {text_color};
            }}
        """)
        
        # Estilo para el contenido
        if hasattr(self, 'content_widget'):
            self.content_widget.setStyleSheet(f"""
                QWidget {{
                    background: {bg_color};
                    color: {text_color};
                }}
            """)
        
        # Estilo para el scroll area
        self.scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: {bg_color};
            }}
            QScrollBar:vertical {{
                border: none;
                background: {hover_color};
                width: 8px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {secondary_text};
                min-height: 40px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
            QScrollBar:horizontal {{
                height: 0px;
                background: transparent;
            }}
        """)
        
        # Estilo para el título
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 18px;
                    font-weight: bold;
                    color: {accent_color};
                }}
            """)
        
        # Estilo para el contador
        if hasattr(self, 'count_label'):
            self.count_label.setStyleSheet(f"""
                QLabel {{
                    color: {secondary_text};
                }}
            """)
        
        # Estilo para las etiquetas de fechas
        if hasattr(self, 'dates_label'):
            self.dates_label.setStyleSheet(f"""
                QLabel {{
                    font-weight: bold;
                    color: {secondary_text};
                }}
            """)
        
        # Estilo para el scroll de fechas
        if hasattr(self, 'dates_scroll'):
            self.dates_scroll.setStyleSheet(f"""
                QScrollArea {{
                    border: 1px solid {border_color};
                    border-radius: 4px;
                    background: {bg_color};
                }}
            """)
        
        # Estilo para las fechas individuales
        if hasattr(self, 'date_labels'):
            for label in self.date_labels:
                label.setStyleSheet(f"""
                    QLabel {{
                        color: {secondary_text};
                    }}
                """)
        
        # Estilo para el ID
        if hasattr(self, 'id_label'):
            self.id_label.setStyleSheet(f"""
                QLabel {{
                    color: {secondary_text};
                    font-family: monospace;
                }}
            """)
        
        # Estilo para el color ID
        if hasattr(self, 'color_label'):
            self.color_label.setStyleSheet(f"""
                QLabel {{
                    color: {secondary_text};
                }}
            """)
        
        # Estilo para las etiquetas de tags
        if hasattr(self, 'tags_label'):
            self.tags_label.setStyleSheet(f"""
                QLabel {{
                    font-weight: bold;
                    color: {secondary_text};
                }}
            """)
        
        # Estilo para los tags individuales
        if hasattr(self, 'tag_labels'):
            tag_bg = "#303134" if is_dark else "#e8f0fe"
            tag_color = accent_color
            for label in self.tag_labels:
                label.setStyleSheet(f"""
                    QLabel {{
                        background: {tag_bg};
                        color: {tag_color};
                        padding: 2px 8px;
                        border-radius: 10px;
                    }}
                """)
        
        # Estilo para la etiqueta de descripción
        if hasattr(self, 'desc_title_label'):
            self.desc_title_label.setStyleSheet(f"""
                QLabel {{
                    font-weight: bold;
                    color: {secondary_text};
                }}
            """)
        
        # Estilo para el texto de descripción
        if hasattr(self, 'desc_text'):
            self.desc_text.setStyleSheet(f"""
                QTextEdit {{
                    border: 1px solid {border_color};
                    border-radius: 4px;
                    padding: 8px;
                    background: {bg_color};
                    color: {text_color};
                }}
                QTextEdit:hover {{
                    border-color: {accent_color};
                }}
            """)
        
        # Estilo para la etiqueta de datos raw
        if hasattr(self, 'raw_label'):
            self.raw_label.setStyleSheet(f"""
                QLabel {{
                    font-weight: bold;
                    color: {secondary_text};
                }}
            """)
        
        # Estilo para el texto raw
        if hasattr(self, 'raw_text'):
            raw_bg = "#1e1e1e" if is_dark else "#f8f9fa"
            self.raw_text.setStyleSheet(f"""
                QTextEdit {{
                    font-family: monospace;
                    border: 1px solid {border_color};
                    border-radius: 4px;
                    padding: 8px;
                    color: {text_color};
                    background: {raw_bg};
                }}
                QTextEdit:hover {{
                    border-color: {accent_color};
                }}
            """)
            
    def update_theme(self):
        """Actualiza los estilos cuando cambia el tema"""
        self.apply_theme() 