from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QWidget,
    QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import os
from datetime import datetime

class EventDetailsDialog(QDialog):
    def __init__(self, events, parent=None):
        super().__init__(parent)
        self.events = events if isinstance(events, list) else [events]
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Detalles del Evento")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Contenedor principal con scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: white;
            }
        """)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)

        # Título del evento
        title_container = QHBoxLayout()
        
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'event_icon.svg')
        icon_label.setPixmap(QIcon(icon_path).pixmap(24, 24))
        title_container.addWidget(icon_label)

        # Si solo hay un evento, no mostrar el contador
        if len(self.events) == 1:
            title_label = QLabel(self.events[0].title)
        else:
            title_label = QLabel(f"{self.events[0].title} (Se repite {len(self.events)} veces)")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #1a73e8;
            }
        """)
        title_container.addWidget(title_label)
        title_container.addStretch()
        
        content_layout.addLayout(title_container)

        # Fechas de los eventos con scroll si son muchas
        dates_widget = QWidget()
        dates_layout = QVBoxLayout(dates_widget)
        dates_layout.setSpacing(5)
        
        dates_label = QLabel("Fechas de ejecución:")
        dates_label.setStyleSheet("font-weight: bold; color: #5f6368;")
        
        dates_scroll = QScrollArea()
        dates_scroll.setWidgetResizable(True)
        dates_scroll.setMaximumHeight(150)  # Altura máxima
        dates_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #dadce0;
                border-radius: 4px;
                background: white;
            }
        """)
        
        dates_container = QWidget()
        dates_container_layout = QVBoxLayout(dates_container)
        
        for event in self.events:
            date_text = f"• {event.start_datetime.strftime('%d/%m/%Y %H:%M')} - {event.end_datetime.strftime('%H:%M')}"
            date_label = QLabel(date_text)
            date_label.setStyleSheet("color: #5f6368;")
            dates_container_layout.addWidget(date_label)
        
        dates_scroll.setWidget(dates_container)
        dates_layout.addWidget(dates_label)
        dates_layout.addWidget(dates_scroll)
        content_layout.addWidget(dates_widget)

        # ID del evento
        id_label = QLabel(f"ID: {self.events[0].google_event_id or 'No disponible'}")
        id_label.setStyleSheet("color: #666; font-family: monospace;")
        content_layout.addWidget(id_label)

        # Color ID
        if hasattr(self.events[0], 'colorId'):
            color_label = QLabel(f"Color ID: {self.events[0].colorId}")
            color_label.setStyleSheet("color: #666;")
            content_layout.addWidget(color_label)

        # Tags
        if hasattr(self.events[0], 'tags') and self.events[0].tags:
            tags_container = QHBoxLayout()
            tags_label = QLabel("Tags:")
            tags_label.setStyleSheet("font-weight: bold; color: #5f6368;")
            tags_container.addWidget(tags_label)
            
            for tag in self.events[0].tags:
                tag_label = QLabel(tag)
                tag_label.setStyleSheet("""
                    QLabel {
                        background: #e8f0fe;
                        color: #1a73e8;
                        padding: 2px 8px;
                        border-radius: 10px;
                    }
                """)
                tags_container.addWidget(tag_label)
            tags_container.addStretch()
            content_layout.addLayout(tags_container)

        # Descripción con formato HTML
        if self.events[0].description:
            desc_label = QLabel("Descripción:")
            desc_label.setStyleSheet("font-weight: bold; color: #5f6368;")
            content_layout.addWidget(desc_label)
            
            desc_text = QTextEdit()
            desc_text.setHtml(self.events[0].description)
            desc_text.setReadOnly(True)
            desc_text.setMinimumHeight(100)
            desc_text.setMaximumHeight(200)
            desc_text.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #dadce0;
                    border-radius: 4px;
                    padding: 8px;
                    background: white;
                    color: #333;
                }
                QTextEdit:hover {
                    border-color: #1a73e8;
                }
            """)
            content_layout.addWidget(desc_text)

        # JSON Raw Data
        raw_label = QLabel("Datos JSON:")
        raw_label.setStyleSheet("font-weight: bold; color: #5f6368;")
        content_layout.addWidget(raw_label)
        
        raw_text = QTextEdit()
        raw_text.setPlainText(str(self.events[0].__dict__))
        raw_text.setReadOnly(True)
        raw_text.setMinimumHeight(100)
        raw_text.setMaximumHeight(200)
        raw_text.setStyleSheet("""
            QTextEdit {
                font-family: monospace;
                border: 1px solid #dadce0;
                border-radius: 4px;
                padding: 8px;
                color: #333;
                background: #f8f9fa;
            }
            QTextEdit:hover {
                border-color: #1a73e8;
            }
        """)
        content_layout.addWidget(raw_text)

        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Botón de cerrar
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
            QPushButton {
                background: #1a73e8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: #1557b0;
            }
        """)
        
        button_container = QHBoxLayout()
        button_container.addStretch()
        button_container.addWidget(close_button)
        layout.addLayout(button_container)

        self.setStyleSheet("""
            QDialog {
                background: white;
            }
        """) 