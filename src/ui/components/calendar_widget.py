from PyQt6.QtWidgets import (
    QWidget, QCalendarWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QStackedWidget, QGridLayout, QLabel,
    QScrollArea
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QLocale, QTimer
from PyQt6.QtGui import QIcon
from models.event import Event
from config.settings import Settings
from typing import List
from datetime import datetime, date, timezone, timedelta
from .day_cell_widget import (
    DayCellWidget, EventLabel, 
    DetailedEventWidget, EventsDialog
)
from ..styles.theme import Theme
import logging
import os

logger = logging.getLogger(__name__)

class CalendarWidget(QWidget):
    eventClicked = pyqtSignal(Event)
    dateSelected = pyqtSignal(date)
    monthChanged = pyqtSignal(datetime)
    refreshRequested = pyqtSignal()

    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.parent = parent
        self.settings = settings or Settings()
        self.settings.settingsChanged.connect(self.on_settings_changed)
        self.events = []
        self.highlighted_events = []  # Store highlighted events
        self.current_view = 'month'  # Default view
        self.current_date = QDate.currentDate()
        self.header_label = None
        self.prev_btn = None
        self.next_btn = None
        self.today_btn = None
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.check_and_refresh)
        self.setObjectName("calendar_widget")  # Set object name for CSS styling
        self.init_ui()
        self.update_auto_refresh()
        self.check_and_refresh()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header con mes y año
        header_layout = QHBoxLayout()
        
        self.header_label = QLabel()
        self.header_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #3c4043;
                padding: 5px 15px;
                background: #f8f9fa;
            }
        """)
        
        # Botones de navegación
        self.prev_btn = QPushButton("<")
        self.prev_btn.setFixedSize(30, 30)
        self.prev_btn.clicked.connect(self.previous_period)
        
        self.next_btn = QPushButton(">")
        self.next_btn.setFixedSize(30, 30)
        self.next_btn.clicked.connect(self.next_period)
        
        self.today_btn = QPushButton("Hoy")
        self.today_btn.clicked.connect(self.go_to_today)
        
        # Selector de vista
        self.view_selector = QComboBox()
        self.view_selector.addItems(["Mes", "Semana", "Día"])
        self.view_selector.currentTextChanged.connect(self.change_view)
        
        # Botón de actualización
        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'refresh_icon.svg')))
        self.refresh_btn.setFixedSize(30, 30)
        self.refresh_btn.clicked.connect(self.request_refresh)
        
        # Añadir widgets al layout del header
        header_layout.addWidget(self.prev_btn)
        header_layout.addWidget(self.next_btn)
        header_layout.addWidget(self.today_btn)
        header_layout.addWidget(self.header_label)
        header_layout.addStretch()
        header_layout.addWidget(self.view_selector)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Stack para las diferentes vistas
        self.view_stack = QStackedWidget()
        
        # Contenedor para la vista de mes
        self.month_container = QWidget()
        month_layout = QVBoxLayout(self.month_container)
        month_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area para la vista de mes
        self.month_scroll = QScrollArea()
        self.month_scroll.setWidgetResizable(True)
        self.month_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        month_layout.addWidget(self.month_scroll)
        
        # Contenedor para la vista de semana
        self.week_container = QWidget()
        week_layout = QVBoxLayout(self.week_container)
        week_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area para la vista de semana
        self.week_scroll = QScrollArea()
        self.week_scroll.setWidgetResizable(True)
        self.week_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        week_layout.addWidget(self.week_scroll)
        
        # Contenedor para la vista de día
        self.day_container = QWidget()
        day_layout = QVBoxLayout(self.day_container)
        day_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area para la vista de día
        self.day_scroll = QScrollArea()
        self.day_scroll.setWidgetResizable(True)
        self.day_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        day_layout.addWidget(self.day_scroll)
        
        # Añadir contenedores al stack
        self.view_stack.addWidget(self.month_container)
        self.view_stack.addWidget(self.week_container)
        self.view_stack.addWidget(self.day_container)
        
        layout.addWidget(self.view_stack)

    def set_events(self, events: List[Event]):
        """Actualiza la lista de eventos y refresca la vista"""
        self.events = events
        self.refresh_view()

    def refresh_view(self):
        """Refresca la vista actual con los eventos"""
        if self.current_view == 'month':
            self.refresh_month_view(self.highlighted_events)
        elif self.current_view == 'week':
            self.refresh_week_view(self.highlighted_events)
        else:
            self.refresh_day_view(self.highlighted_events)

    def _update_header(self):
        """Actualiza el header con el mes y año actual"""
        locale = QLocale()
        month_name = locale.monthName(self.current_date.month())
        year = self.current_date.year()
        self.header_label.setText(f"{month_name} {year}")

    def refresh_month_view(self, highlighted_events):
        """Refresca la vista de mes"""
        self._update_header()
        
        # Limpiar la vista actual
        if hasattr(self, 'month_grid'):
            QWidget().setLayout(self.month_grid)
        
        # Crear nuevo grid
        self.month_grid = QGridLayout()
        self.month_grid.setSpacing(0)
        
        # Obtener el primer día del mes
        first_day = QDate(self.current_date.year(), self.current_date.month(), 1)
        
        # Calcular el número de días en el mes
        days_in_month = first_day.daysInMonth()
        
        # Obtener el día de la semana del primer día (0=lunes, 6=domingo)
        first_day_of_week = first_day.dayOfWeek() % 7
        
        # Añadir cabeceras de días de la semana
        days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        for i, day in enumerate(days):
            label = QLabel(day)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Aplicar estilo basado en el tema actual
            is_dark = Theme.is_dark_mode
            text_color = Theme.DARK_TEXT if is_dark else Theme.LIGHT_TEXT
            
            label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color};
                    font-weight: bold;
                    padding: 5px;
                    background: transparent;
                }}
            """)
            
            self.month_grid.addWidget(label, 0, i)
        
        # Añadir celdas de días
        row = 1
        col = first_day_of_week
        
        # Verificar si highlighted_events es None y convertirlo a lista vacía si es necesario
        if highlighted_events is None:
            highlighted_events = []
        
        for day in range(1, days_in_month + 1):
            date = QDate(self.current_date.year(), self.current_date.month(), day)
            
            # Filtrar eventos para este día
            day_events = [e for e in self.events if self._event_on_date(e, date)]
            
            # Verificar si algún evento de este día está en la lista de eventos resaltados
            has_highlighted_event = any(e in highlighted_events for e in day_events)
            
            # Crear celda de día
            day_cell = self._create_day_cell(date, day_events, has_highlighted_event)
            
            self.month_grid.addWidget(day_cell, row, col)
            
            col += 1
            if col > 6:
                col = 0
                row += 1
        
        # Crear widget para la vista de mes
        month_widget = QWidget()
        month_widget.setLayout(self.month_grid)
        
        # Añadir widget al scroll area
        self.month_scroll.setWidget(month_widget)
        
        # Mostrar la vista de mes
        self.view_stack.setCurrentWidget(self.month_container)

    def _create_day_cell(self, date, events, is_highlighted=False):
        """Crea una celda para un día en la vista de mes"""
        cell = QWidget()
        layout = QVBoxLayout(cell)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        
        # Etiqueta para el número de día
        day_label = QLabel(str(date.day()))
        day_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Aplicar estilo basado en el tema actual
        is_dark = Theme.is_dark_mode
        text_color = Theme.DARK_TEXT if is_dark else Theme.LIGHT_TEXT
        bg_color = Theme.DARK_BG if is_dark else Theme.LIGHT_BG
        border_color = Theme.DARK_BORDER if is_dark else Theme.LIGHT_BORDER
        accent_color = Theme.DARK_ACCENT if is_dark else Theme.LIGHT_ACCENT
        
        # Verificar si es el día actual
        is_today = date == QDate.currentDate()
        
        # Verificar si es el día seleccionado
        is_selected = date == self.current_date
        
        # Estilo para el día actual
        if is_today:
            day_label.setStyleSheet(f"""
                QLabel {{
                    color: white;
                    background-color: {accent_color};
                    border-radius: 12px;
                    padding: 2px 6px;
                    font-weight: bold;
                }}
            """)
        else:
            day_label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color};
                    padding: 2px;
                }}
            """)
        
        layout.addWidget(day_label)
        
        # Añadir eventos del día (máximo 3)
        event_count = 0
        for event in events[:3]:
            event_label = QLabel(event.title)
            event_label.setToolTip(event.title)
            
            # Obtener color del evento
            event_style = Theme.get_event_style(event.color_id)
            
            # Aplicar estilo adicional si el evento está resaltado
            if is_highlighted and event in self.highlighted_events:
                event_style += """
                    border: 2px solid #FF5722;
                    font-weight: bold;
                """
            
            event_label.setStyleSheet(f"""
                QLabel {{
                    {event_style}
                    border-radius: 2px;
                    padding: 2px 4px;
                    font-size: 10px;
                    margin-top: 1px;
                }}
            """)
            
            event_label.setMaximumHeight(18)
            event_label.setWordWrap(False)
            event_label.setTextFormat(Qt.TextFormat.PlainText)
            
            # Truncar texto largo
            metrics = event_label.fontMetrics()
            text = metrics.elidedText(event.title, Qt.TextElideMode.ElideRight, 80)
            event_label.setText(text)
            
            layout.addWidget(event_label)
            event_count += 1
        
        # Si hay más eventos, mostrar indicador
        if len(events) > 3:
            more_label = QLabel(f"+{len(events) - 3} más")
            more_label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color};
                    font-size: 9px;
                    padding: 1px;
                    text-decoration: underline;
                }}
            """)
            more_label.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Create a custom click handler for the "more" label
            def show_events_dialog(e, date=date, events=events):
                # Convert QDate to datetime
                py_date = datetime(date.year(), date.month(), date.day())
                
                # Separate all-day and timed events
                all_day_events = []
                timed_events = []
                
                for event in events:
                    if event.is_all_day:
                        all_day_events.append(event)
                    else:
                        timed_events.append(event)
                
                # Create and show the events dialog
                from .day_cell_widget import EventsDialog
                dialog = EventsDialog(py_date, {'all_day': all_day_events, 'timed': timed_events}, self)
                dialog.exec()
            
            # Assign the custom click handler
            more_label.mousePressEvent = show_events_dialog
            
            layout.addWidget(more_label)
        
        # Añadir espacio en blanco para completar la celda
        layout.addStretch()
        
        # Estilo para la celda
        cell_style = f"""
            QWidget {{
                background-color: {bg_color};
                border: 1px solid {border_color};
            }}
        """
        
        # Si es el día seleccionado, añadir borde resaltado
        if is_selected:
            cell_style = f"""
                QWidget {{
                    background-color: {bg_color};
                    border: 2px solid {accent_color};
                }}
            """
        
        # Si tiene eventos resaltados, añadir fondo especial
        if is_highlighted:
            highlight_bg = f"{accent_color}15"  # Color con 15% de opacidad
            cell_style = f"""
                QWidget {{
                    background-color: {highlight_bg};
                    border: 2px solid {accent_color};
                }}
            """
        
        cell.setStyleSheet(cell_style)
        
        # Hacer que la celda sea clickeable
        cell.mousePressEvent = lambda e, date=date: self.on_date_selected(date)
        cell.setCursor(Qt.CursorShape.PointingHandCursor)
        
        return cell

    def find_event_widget(self, event):
        """Encuentra el widget de un evento específico"""
        # Implementar la lógica para encontrar el widget del evento
        # en la vista actual
        pass

    def refresh_week_view(self, highlighted_events):
        """Refresca la vista de semana"""
        self._update_header()
        
        # Limpiar la vista actual
        if hasattr(self, 'week_grid'):
            QWidget().setLayout(self.week_grid)
        
        # Crear nuevo grid
        self.week_grid = QGridLayout()
        self.week_grid.setSpacing(0)
        
        # Obtener el primer día de la semana (lunes)
        current_date = self.current_date
        days_to_monday = current_date.dayOfWeek() - 1
        first_day_of_week = current_date.addDays(-days_to_monday)
        
        # Verificar si highlighted_events es None y convertirlo a lista vacía si es necesario
        if highlighted_events is None:
            highlighted_events = []
        
        # Añadir cabeceras de horas en la primera columna
        for hour in range(24):
            hour_label = QLabel(f"{hour}:00")
            hour_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            # Aplicar estilo basado en el tema actual
            is_dark = Theme.is_dark_mode
            text_color = Theme.DARK_TEXT if is_dark else Theme.LIGHT_TEXT
            
            hour_label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color};
                    padding: 5px;
                    font-size: 12px;
                }}
            """)
            
            self.week_grid.addWidget(hour_label, hour + 1, 0)
        
        # Añadir cabeceras de días en la primera fila
        days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        for i, day_name in enumerate(days):
            date = first_day_of_week.addDays(i)
            
            # Crear widget para la cabecera del día
            day_header = QWidget()
            day_layout = QVBoxLayout(day_header)
            day_layout.setContentsMargins(5, 5, 5, 5)
            
            # Etiqueta para el nombre del día
            day_label = QLabel(day_name)
            day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Etiqueta para el número del día
            date_label = QLabel(str(date.day()))
            date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Aplicar estilo basado en el tema actual
            is_dark = Theme.is_dark_mode
            text_color = Theme.DARK_TEXT if is_dark else Theme.LIGHT_TEXT
            bg_color = Theme.DARK_BG if is_dark else Theme.LIGHT_BG
            border_color = Theme.DARK_BORDER if is_dark else Theme.LIGHT_BORDER
            accent_color = Theme.DARK_ACCENT if is_dark else Theme.LIGHT_ACCENT
            
            # Verificar si es el día actual
            is_today = date == QDate.currentDate()
            
            if is_today:
                date_label.setStyleSheet(f"""
                    QLabel {{
                        color: white;
                        background-color: {accent_color};
                        border-radius: 12px;
                        padding: 2px 6px;
                        font-weight: bold;
                        font-size: 14px;
                    }}
                """)
            else:
                date_label.setStyleSheet(f"""
                    QLabel {{
                        color: {text_color};
                        font-size: 14px;
                    }}
                """)
            
            day_label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color};
                    font-weight: bold;
                }}
            """)
            
            day_layout.addWidget(day_label)
            day_layout.addWidget(date_label)
            
            self.week_grid.addWidget(day_header, 0, i + 1)
            
            # Añadir celdas para cada hora del día
            for hour in range(24):
                # Crear celda para la hora
                hour_cell = QWidget()
                cell_layout = QVBoxLayout(hour_cell)
                cell_layout.setContentsMargins(2, 2, 2, 2)
                cell_layout.setSpacing(0)
                
                # Filtrar eventos para esta hora y día
                hour_events = []
                for event in self.events:
                    event_date = QDate(
                        event.start_datetime.year,
                        event.start_datetime.month,
                        event.start_datetime.day
                    )
                    
                    if event_date == date:
                        # Verificar si el evento ocurre en esta hora
                        event_start_hour = event.start_datetime.hour
                        event_end_hour = event.end_datetime.hour
                        
                        if event_start_hour <= hour <= event_end_hour:
                            hour_events.append(event)
                
                # Verificar si algún evento de esta hora está en la lista de eventos resaltados
                has_highlighted_event = any(e in highlighted_events for e in hour_events)
                
                # Añadir eventos a la celda
                for event in hour_events:
                    event_label = QLabel(event.title)
                    event_label.setToolTip(event.title)
                    
                    # Obtener color del evento
                    event_style = Theme.get_event_style(event.color_id)
                    
                    # Aplicar estilo adicional si el evento está resaltado
                    if event in highlighted_events:
                        event_style += """
                            border: 2px solid #FF5722;
                            font-weight: bold;
                        """
                    
                    event_label.setStyleSheet(f"""
                        QLabel {{
                            {event_style}
                            border-radius: 2px;
                            padding: 2px 4px;
                            font-size: 10px;
                            margin-top: 1px;
                        }}
                    """)
                    
                    event_label.setMaximumHeight(18)
                    event_label.setWordWrap(False)
                    event_label.setTextFormat(Qt.TextFormat.PlainText)
                    
                    # Truncar texto largo
                    metrics = event_label.fontMetrics()
                    text = metrics.elidedText(event.title, Qt.TextElideMode.ElideRight, 80)
                    event_label.setText(text)
                    
                    cell_layout.addWidget(event_label)
                
                # Añadir espacio en blanco para completar la celda
                cell_layout.addStretch()
                
                # Estilo para la celda
                cell_style = f"""
                    QWidget {{
                        background-color: {bg_color};
                        border: 1px solid {border_color};
                    }}
                """
                
                # Si tiene eventos resaltados, añadir fondo especial
                if has_highlighted_event:
                    highlight_bg = f"{accent_color}15"  # Color con 15% de opacidad
                    cell_style = f"""
                        QWidget {{
                            background-color: {highlight_bg};
                            border: 1px solid {accent_color};
                        }}
                    """
                
                hour_cell.setStyleSheet(cell_style)
                
                # Hacer que la celda sea clickeable
                hour_cell.mousePressEvent = lambda e, date=date: self.on_date_selected(date)
                hour_cell.setCursor(Qt.CursorShape.PointingHandCursor)
                
                self.week_grid.addWidget(hour_cell, hour + 1, i + 1)
        
        # Crear widget para la vista de semana
        week_widget = QWidget()
        week_widget.setLayout(self.week_grid)
        
        # Añadir widget al scroll area
        self.week_scroll.setWidget(week_widget)
        
        # Mostrar la vista de semana
        self.view_stack.setCurrentWidget(self.week_container)

    def refresh_day_view(self, highlighted_events):
        """Refresca la vista de día"""
        self._update_header()
        
        # Verificar si highlighted_events es None y convertirlo a lista vacía si es necesario
        if highlighted_events is None:
            highlighted_events = []
        
        # Crear nuevo widget para la vista diaria
        day_widget = QWidget()
        day_layout = QVBoxLayout(day_widget)
        day_layout.setContentsMargins(10, 10, 10, 10)
        day_layout.setSpacing(10)
        
        # Aplicar estilo basado en el tema actual
        is_dark = Theme.is_dark_mode
        bg_color = Theme.DARK_BG if is_dark else Theme.LIGHT_BG
        text_color = Theme.DARK_TEXT if is_dark else Theme.LIGHT_TEXT
        border_color = Theme.DARK_BORDER if is_dark else Theme.LIGHT_BORDER
        accent_color = Theme.DARK_ACCENT if is_dark else Theme.LIGHT_ACCENT
        
        # Filtrar eventos para el día seleccionado
        selected_date = self.current_date
        day_events = []
        
        for event in self.events:
            event_date = QDate(
                event.start_datetime.year,
                event.start_datetime.month,
                event.start_datetime.day
            )
            
            if event_date == selected_date:
                day_events.append(event)
        
        # Separar eventos de todo el día y eventos con hora
        all_day_events = []
        timed_events = []
        
        for event in day_events:
            if event.is_all_day:
                all_day_events.append(event)
            else:
                timed_events.append(event)
        
        # Sección de eventos de todo el día
        if all_day_events:
            # Cabecera para eventos de todo el día
            all_day_header = QLabel("Eventos de todo el día")
            all_day_header.setStyleSheet(Theme.SECTION_HEADER_STYLE)
            day_layout.addWidget(all_day_header)
            
            # Contenedor para eventos de todo el día
            all_day_container = QWidget()
            all_day_layout = QVBoxLayout(all_day_container)
            all_day_layout.setContentsMargins(0, 0, 0, 0)
            all_day_layout.setSpacing(5)
            
            # Añadir eventos de todo el día
            for event in all_day_events:
                event_widget = QLabel(event.title)
                
                # Obtener color del evento
                event_style = Theme.get_event_style(event.color_id)
                
                # Aplicar estilo adicional si el evento está resaltado
                if event in highlighted_events:
                    event_style += """
                        border: 2px solid #FF5722;
                        font-weight: bold;
                    """
                
                event_widget.setStyleSheet(f"""
                    QLabel {{
                        {event_style}
                        border-radius: 4px;
                        padding: 8px 12px;
                        font-size: 13px;
                    }}
                """)
                
                all_day_layout.addWidget(event_widget)
            
            day_layout.addWidget(all_day_container)
            day_layout.addSpacing(10)
        
        # Sección de eventos con hora
        if timed_events:
            # Cabecera para eventos con hora
            timed_header = QLabel("Eventos programados")
            timed_header.setStyleSheet(Theme.SECTION_HEADER_STYLE)
            day_layout.addWidget(timed_header)
            
            # Contenedor para eventos con hora
            timed_container = QWidget()
            timed_layout = QGridLayout(timed_container)
            timed_layout.setContentsMargins(0, 0, 0, 0)
            timed_layout.setSpacing(5)
            
            # Organizar eventos por hora
            hour_events = {}
            for hour in range(24):
                hour_events[hour] = []
            
            for event in timed_events:
                hour = event.start_datetime.hour
                hour_events[hour].append(event)
            
            # Añadir eventos por hora
            row = 0
            for hour in range(24):
                if hour_events[hour]:
                    # Etiqueta de hora
                    hour_label = QLabel(f"{hour:02d}:00")
                    hour_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
                    hour_label.setStyleSheet(f"""
                        QLabel {{
                            color: {text_color};
                            font-weight: bold;
                            padding: 5px;
                        }}
                    """)
                    
                    timed_layout.addWidget(hour_label, row, 0)
            
                    # Contenedor para eventos de esta hora
                    hour_container = QWidget()
                    hour_layout = QVBoxLayout(hour_container)
                    hour_layout.setContentsMargins(0, 0, 0, 0)
                    hour_layout.setSpacing(5)
                    
                    # Añadir eventos de esta hora
                    for event in hour_events[hour]:
                        event_widget = QLabel(f"{event.start_datetime.strftime('%H:%M')} - {event.end_datetime.strftime('%H:%M')} {event.title}")
                        
                        # Obtener color del evento
                        event_style = Theme.get_event_style(event.color_id)
                        
                        # Aplicar estilo adicional si el evento está resaltado
                        if event in highlighted_events:
                            event_style += """
                                border: 2px solid #FF5722;
                                font-weight: bold;
                            """
                        
                        event_widget.setStyleSheet(f"""
                            QLabel {{
                                {event_style}
                                border-radius: 4px;
                                padding: 8px 12px;
                                font-size: 13px;
                            }}
                        """)
                        
                    hour_layout.addWidget(event_widget)
                    
                    timed_layout.addWidget(hour_container, row, 1)
                    row += 1
            
            day_layout.addWidget(timed_container)
        
        # Si no hay eventos, mostrar mensaje
        if not day_events:
            no_events = QLabel("No hay eventos para este día")
            no_events.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_events.setStyleSheet(f"""
                QLabel {{
                    color: {text_color};
                    font-size: 14px;
                    padding: 20px;
                }}
            """)
            day_layout.addWidget(no_events)
        
        # Añadir espacio en blanco al final
        day_layout.addStretch()
        
        # Añadir widget al scroll area
        self.day_scroll.setWidget(day_widget)
        
        # Mostrar la vista de día
        self.view_stack.setCurrentWidget(self.day_container)

    def change_view(self, view_text: str):
        """Cambia entre las diferentes vistas"""
        view_map = {'Mes': 'month', 'Semana': 'week', 'Día': 'day'}
        self.current_view = view_map[view_text]
        
        # Limpiar eventos resaltados al cambiar a vista mensual
        if self.current_view == 'month':
            self.highlighted_events = []
        
        self.refresh_view()

    def previous_period(self):
        """Va al período anterior"""
        if self.current_view == 'month':
            self.current_date = self.current_date.addMonths(-1)
        elif self.current_view == 'week':
            self.current_date = self.current_date.addDays(-7)
        else:  # day view
            self.current_date = self.current_date.addDays(-1)
        
        # Emitir señal de cambio de mes si es necesario
        if self.current_view == 'month':
            self.monthChanged.emit(datetime(
                self.current_date.year(),
                self.current_date.month(),
                1,
                tzinfo=timezone.utc
            ))
        
        self.refresh_view()

    def next_period(self):
        """Va al período siguiente"""
        if self.current_view == 'month':
            self.current_date = self.current_date.addMonths(1)
        elif self.current_view == 'week':
            self.current_date = self.current_date.addDays(7)
        else:  # day view
            self.current_date = self.current_date.addDays(1)
        
        # Emitir señal de cambio de mes si es necesario
        if self.current_view == 'month':
            self.monthChanged.emit(datetime(
                self.current_date.year(),
                self.current_date.month(),
                1,
                tzinfo=timezone.utc
            ))
        
        self.refresh_view()

    def go_to_today(self):
        """Va a la fecha actual"""
        self.current_date = QDate.currentDate()
        self.refresh_view()

    def on_date_selected(self, qdate: QDate):
        """Maneja la selección de una fecha"""
        selected_date = date(qdate.year(), qdate.month(), qdate.day())
        self.dateSelected.emit(selected_date)
        
        # Encuentra eventos para la fecha seleccionada
        day_events = [
            event for event in self.events
            if event.start_datetime.date() == selected_date
        ]
        
        # TODO: Mostrar eventos del día seleccionado 

    def request_refresh(self):
        """Solicita una actualización de eventos"""
        self.refreshRequested.emit()

    def check_and_refresh(self):
        """Verifica si el auto-refresh está habilitado antes de refrescar"""
        if self.settings.auto_refresh_enabled:
            logger.info("Ejecutando auto-refresh programado")
            self.request_refresh()
        else:
            logger.info("Auto-refresh deshabilitado, deteniendo timer")
            self.refresh_timer.stop()

    def update_auto_refresh(self):
        """Actualiza el estado del auto-refresh según la configuración"""
        if self.settings.auto_refresh_enabled:
            if not self.refresh_timer.isActive():
                logger.info("Iniciando auto-refresh timer")
                self.refresh_timer.start(20000)
        else:
            if self.refresh_timer.isActive():
                logger.info("Deteniendo auto-refresh timer")
                self.refresh_timer.stop()

    def on_settings_changed(self):
        """Actualiza la configuración cuando cambia"""
        self.update_auto_refresh()
        
    def update_theme(self):
        """Update the widget's appearance when the theme changes"""
        # Determinar colores basados en el tema actual
        is_dark = Theme.is_dark_mode
        text_color = Theme.DARK_TEXT if is_dark else Theme.LIGHT_TEXT
        bg_color = Theme.DARK_BG if is_dark else Theme.LIGHT_BG
        border_color = Theme.DARK_BORDER if is_dark else Theme.LIGHT_BORDER
        
        # Update header label
        if self.header_label:
            self.header_label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color};
                    font-size: 16px;
                    font-weight: bold;
                    padding: 8px;
                    background-color: {bg_color};
                }}
            """)
            
        # Update navigation buttons
        for btn in [self.prev_btn, self.next_btn, self.today_btn]:
            if btn:
                btn.setStyleSheet(Theme.BUTTON_STYLE)
        
        # Update main container background
        self.setStyleSheet(f"""
            QWidget#calendar_widget {{
                background-color: {bg_color};
            }}
            QScrollArea {{
                background-color: {bg_color};
                border: none;
            }}
        """)
        
        # Update scroll areas
        for scroll_area in [self.month_scroll, self.week_scroll, self.day_scroll]:
            if scroll_area:
                scroll_area.setStyleSheet(f"""
                    QScrollArea {{
                        background-color: {bg_color};
                        border: none;
                    }}
                    QWidget {{
                        background-color: {bg_color};
                    }}
                """)
                
        # Refresh the view to update all cells
        self.refresh_view()
        
    def highlight_events(self, events):
        """Resalta eventos específicos en el calendario
        
        Args:
            events (list): Lista de eventos a resaltar
        """
        # Si recibimos un solo evento (no una lista), convertirlo a lista
        if not isinstance(events, list):
            events = [events]
            
        if not events:
            logger.warning("No hay eventos para resaltar")
            return
            
        # Guardar los eventos resaltados
        self.highlighted_events = events
        
        # Tomamos el primer evento para navegar a su fecha
        event = events[0]
        
        logger.info(f"Resaltando {len(events)} eventos. Primer evento: {event.title}")
        
        # Obtener la fecha del evento
        event_date = QDate(
            event.start_datetime.year,
            event.start_datetime.month,
            event.start_datetime.day
        )
        
        # Actualizar la fecha actual pero mantener la vista actual
        self.current_date = event_date
        
        # Refrescar la vista para mostrar los eventos resaltados
        self.refresh_view()
        
        # No emitimos la señal de selección de fecha para evitar efectos secundarios
        # que podrían causar problemas con la selección de fecha

    def clear_events(self):
        """Limpia todos los eventos del calendario"""
        self.events = []
        self.refresh_view()

    def _event_on_date(self, event, date):
        """Verifica si un evento ocurre en una fecha específica"""
        event_start = QDate(
            event.start_datetime.year,
            event.start_datetime.month,
            event.start_datetime.day
        )
        event_end = QDate(
            event.end_datetime.year,
            event.end_datetime.month,
            event.end_datetime.day
        )
        
        # Verificar si la fecha está dentro del rango del evento
        return event_start <= date <= event_end 