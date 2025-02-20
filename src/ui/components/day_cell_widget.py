from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, 
    QDialog, QScrollArea, QHBoxLayout, QApplication
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPainter, QColor, QPen
from models.event import Event
from typing import List, Dict
from datetime import datetime, timezone
from ui.styles.theme import Theme
from PyQt6.QtCore import QTimer

class CopyButton(QPushButton):
    def __init__(self, text_to_copy: str, parent=None):
        super().__init__("📋", parent)
        self.text_to_copy = text_to_copy
        self.setToolTip("Copiar ID")
        self.clicked.connect(self.copy_to_clipboard)
        self.setFixedSize(24, 24)
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #dadce0;
                border-radius: 12px;
                padding: 2px;
            }
            QPushButton:hover {
                background: #f1f3f4;
            }
        """)

    def copy_to_clipboard(self):
        QApplication.clipboard().setText(self.text_to_copy)
        self.setText("✓")
        QTimer.singleShot(1000, lambda: self.setText("📋"))

class DetailedEventWidget(QWidget):
    def __init__(self, event: Event, parent=None):
        super().__init__(parent)
        self.event = event
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)

        # Header con título y botón de copiar
        header = QHBoxLayout()
        
        # Título y hora
        title_text = self.event.title
        if not self.event.is_all_day():
            start_time = self.event.start_datetime.strftime("%H:%M")
            end_time = self.event.end_datetime.strftime("%H:%M")
            title_text = f"{start_time}-{end_time} {title_text}"
        
        title = QLabel(title_text)
        title.setStyleSheet("font-weight: bold;")
        header.addWidget(title, stretch=1)
        
        # Botón de copiar ID
        copy_btn = CopyButton(self.event.google_event_id)
        header.addWidget(copy_btn)
        
        layout.addLayout(header)

        # Descripción si existe
        if self.event.description:
            desc = QLabel(self.event.description)
            desc.setWordWrap(True)
            desc.setStyleSheet("""
                QLabel {
                    color: #5f6368;
                    padding: 4px;
                    background: #f8f9fa;
                    border-radius: 4px;
                }
            """)
            layout.addWidget(desc)

        # Aplicar estilo según el color del evento
        self.setStyleSheet(f"""
            QWidget {{
                background: white;
                border: 1px solid #dadce0;
                border-radius: 8px;
                {Theme.get_event_style(self.event.color_id)}
            }}
        """)

class EventLabel(QLabel):
    """Widget simple para mostrar eventos en vistas de calendario"""
    def __init__(self, event: Event, parent=None):
        super().__init__(parent)
        self.event = event
        self.init_ui()

    def init_ui(self):
        display_text = self.event.title
        if not self.event.is_all_day():
            start_time = self.event.start_datetime.strftime("%H:%M")
            display_text = f"{start_time} - {display_text}"
        
        self.setText(display_text)
        self.setWordWrap(True)
        
        # Aplicar estilo según el tipo de evento
        if self.event.is_all_day():
            self.setStyleSheet("""
                QLabel {
                    background-color: #e8f0fe;
                    color: #1a73e8;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    color: #3c4043;
                    padding: 4px 8px 4px 20px;
                    font-size: 12px;
                    background: transparent;
                    background-image: url(src/assets/event-dot.svg);
                    background-repeat: no-repeat;
                    background-position: 4px center;
                }
            """)

class EventsDialog(QDialog):
    def __init__(self, date: datetime, events: Dict[str, List[Event]], parent=None):
        super().__init__(parent)
        self.date = date
        self.events = events
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Eventos - {self.date.strftime('%d/%m/%Y')}")
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(12)
        
        # Mostrar eventos de todo el día
        if self.events['all_day']:
            all_day_label = QLabel("Todo el día")
            all_day_label.setStyleSheet("""
                font-weight: bold; 
                color: #3c4043;
                font-size: 14px;
                padding: 4px;
            """)
            scroll_layout.addWidget(all_day_label)
            
            for event in self.events['all_day']:
                event_widget = DetailedEventWidget(event)
                scroll_layout.addWidget(event_widget)
            
            scroll_layout.addSpacing(16)
        
        # Mostrar eventos con hora
        if self.events['timed']:
            timed_label = QLabel("Eventos programados")
            timed_label.setStyleSheet("""
                font-weight: bold; 
                color: #3c4043;
                font-size: 14px;
                padding: 4px;
            """)
            scroll_layout.addWidget(timed_label)
            
            for event in self.events['timed']:
                event_widget = DetailedEventWidget(event)
                scroll_layout.addWidget(event_widget)
        
        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

class DayCellWidget(QWidget):
    def __init__(self, date: datetime, events: List[Event], parent=None):
        super().__init__(parent)
        self.date = date
        self.utc_date = datetime(
            date.year, date.month, date.day, 
            tzinfo=timezone.utc
        )
        self.events = self._organize_events(events)
        self.init_ui()
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _organize_events(self, events: List[Event]) -> Dict[str, List[Event]]:
        """Organiza eventos por tipo"""
        day_events = {
            'all_day': [],
            'timed': []
        }
        
        for event in events:
            event_start = event.start_datetime.astimezone(timezone.utc)
            event_end = event.end_datetime.astimezone(timezone.utc)
            
            if (event_start.date() <= self.utc_date.date() <= event_end.date()):
                # Determinar si es evento de todo el día
                is_all_day = (
                    event_start.hour == 0 and
                    event_end.hour == 23 and
                    event_end.minute == 59
                )
                
                if is_all_day:
                    day_events['all_day'].append(event)
                else:
                    day_events['timed'].append(event)
        
        # Ordenar eventos
        day_events['all_day'].sort(key=lambda e: (e.title, e.start_datetime))
        day_events['timed'].sort(key=lambda e: e.start_datetime)
        
        return day_events

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(1)
        layout.setContentsMargins(1, 1, 1, 1)

        # Fecha del día
        date_label = QLabel(str(self.date.day))
        date_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(date_label)

        # Mostrar eventos de todo el día primero
        all_day_events = self.events['all_day']
        timed_events = self.events['timed']
        
        total_events = len(all_day_events) + len(timed_events)
        shown_events = 0
        max_events = 3

        # Mostrar eventos de todo el día
        for event in all_day_events:
            if shown_events >= max_events:
                break
            event_label = EventLabel(event)
            layout.addWidget(event_label)
            shown_events += 1

        # Mostrar eventos con hora
        for event in timed_events:
            if shown_events >= max_events:
                break
            event_label = EventLabel(event)
            layout.addWidget(event_label)
            shown_events += 1

        # Mostrar indicador de más eventos
        remaining = total_events - shown_events
        if remaining > 0:
            more_button = QPushButton(f"+{remaining} más")
            more_button.setStyleSheet("""
                QPushButton {
                    color: #666;
                    padding: 2px;
                    font-size: 11px;
                    border: none;
                    text-align: left;
                    background: transparent;
                }
                QPushButton:hover {
                    color: #1a73e8;
                }
            """)
            more_button.clicked.connect(self.show_all_events)
            layout.addWidget(more_button)

        layout.addStretch()

    def show_all_events(self):
        """Muestra diálogo con todos los eventos del día"""
        dialog = EventsDialog(self.date, self.events, self)
        dialog.exec()

    def mousePressEvent(self, event):
        """Maneja el clic en la celda"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.show_all_events()

    def paintEvent(self, event):
        """Dibujar borde y fondo de la celda"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Dibujar fondo
        painter.fillRect(self.rect(), QColor("#ffffff"))

        # Dibujar borde
        pen = QPen(QColor("#e0e0e0"))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1)) 