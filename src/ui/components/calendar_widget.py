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

logger = logging.getLogger(__name__)

class CalendarWidget(QWidget):
    eventClicked = pyqtSignal(Event)
    dateSelected = pyqtSignal(date)
    monthChanged = pyqtSignal(datetime)
    refreshRequested = pyqtSignal()

    def __init__(self, settings: Settings = None, parent=None):
        super().__init__(parent)
        self.settings = settings or Settings()
        self.settings.settingsChanged.connect(self.on_settings_changed)
        self.current_view = 'month'
        self.current_date = QDate.currentDate()
        self.events = []
        self.header_label = None
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.check_and_refresh)
        self.init_ui()
        self.update_auto_refresh()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header con mes y año
        header_layout = QHBoxLayout()
        
        self.header_label = QLabel()
        self.header_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #3c4043;
                padding: 10px;
            }
        """)
        
        header_layout.addWidget(self.header_label)
        header_layout.addStretch()
        
        # Toolbar superior
        toolbar = QHBoxLayout()
        
        # Botones de navegación
        prev_button = QPushButton('←')
        next_button = QPushButton('→')
        today_button = QPushButton('Hoy')
        
        for btn in [prev_button, next_button, today_button]:
            btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid #dadce0;
                    border-radius: 4px;
                    padding: 8px 16px;
                    background: white;
                }
                QPushButton:hover {
                    background: #f1f3f4;
                }
            """)
        
        prev_button.clicked.connect(self.previous_period)
        next_button.clicked.connect(self.next_period)
        today_button.clicked.connect(self.go_to_today)
        
        toolbar.addWidget(prev_button)
        toolbar.addWidget(today_button)
        toolbar.addWidget(next_button)
        
        # Selector de vista
        self.view_selector = QComboBox()
        self.view_selector.addItems(['Mes', 'Semana', 'Día'])
        self.view_selector.currentTextChanged.connect(self.change_view)
        toolbar.addWidget(self.view_selector)
        
        # Agregar botón de refresh
        self.refresh_btn = QPushButton()
        self.refresh_btn.setIcon(QIcon("src/assets/refresh.svg"))
        self.refresh_btn.setToolTip("Actualizar calendario")
        self.refresh_btn.setStyleSheet(Theme.ICON_BUTTON_STYLE)
        self.refresh_btn.clicked.connect(self.request_refresh)
        
        # Agregar el botón al toolbar
        toolbar.addWidget(self.refresh_btn)
        
        header_layout.addLayout(toolbar)
        layout.addLayout(header_layout)
        
        # Stack de vistas
        self.view_stack = QStackedWidget()
        
        # Crear contenedores para cada vista
        self.month_container = QWidget()
        self.week_container = QWidget()
        self.day_container = QWidget()
        
        # Agregar los contenedores al stack
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
            self.refresh_month_view()
        elif self.current_view == 'week':
            self.refresh_week_view()
        else:
            self.refresh_day_view()

    def _update_header(self):
        """Actualiza el header con el mes y año actual"""
        locale = QLocale()
        month_name = locale.monthName(self.current_date.month())
        year = self.current_date.year()
        self.header_label.setText(f"{month_name} {year}")

    def refresh_month_view(self):
        """Refresca la vista de mes con los eventos"""
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
        
        # Obtener el día de la semana en que comienza el mes (0 = lunes, 6 = domingo)
        first_day_of_week = first_day.dayOfWeek()
        
        # Agregar encabezados de días
        days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        for i, day in enumerate(days):
            label = QLabel(day)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    padding: 5px;
                    color: #70757a;
                    border-bottom: 1px solid #e0e0e0;
                }
            """)
            self.month_grid.addWidget(label, 0, i)
        
        # Filtrar eventos solo para el mes actual
        month_start = datetime(
            self.current_date.year(),
            self.current_date.month(),
            1,
            tzinfo=timezone.utc
        )
        month_end = (month_start.replace(day=days_in_month)
                    .replace(hour=23, minute=59, second=59))
        
        current_month_events = [
            event for event in self.events
            if (event.start_datetime <= month_end and 
                event.end_datetime >= month_start)
        ]
        
        # Agregar celdas de días
        row = 1
        col = first_day_of_week - 1
        
        for day in range(1, days_in_month + 1):
            date = QDate(self.current_date.year(), self.current_date.month(), day)
            
            cell = DayCellWidget(date.toPyDate(), current_month_events)
            if date == QDate.currentDate():
                cell.setStyleSheet("background-color: #e8f0fe;")
            
            self.month_grid.addWidget(cell, row, col)
            
            col += 1
            if col > 6:
                col = 0
                row += 1
        
        # Establecer el nuevo layout
        month_widget = QWidget()
        month_widget.setLayout(self.month_grid)
        self.view_stack.removeWidget(self.view_stack.widget(0))
        self.view_stack.insertWidget(0, month_widget)
        self.view_stack.setCurrentWidget(month_widget)

    def refresh_week_view(self):
        """Refresca la vista de semana"""
        self._update_header()
        
        # Crear nuevo widget para la vista semanal
        week_widget = QWidget()
        week_layout = QVBoxLayout(week_widget)
        week_layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        
        # Grid para las horas y eventos
        self.week_grid = QGridLayout(scroll_widget)
        self.week_grid.setSpacing(1)
        
        # Obtener el primer día de la semana
        current_weekday = self.current_date.dayOfWeek()
        week_start = self.current_date.addDays(-current_weekday + 1)
        
        # Agregar encabezados de días
        days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        for i, day in enumerate(days):
            date = week_start.addDays(i)
            header = QLabel(f"{day} {date.day()}")
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header.setStyleSheet(Theme.HEADER_STYLE)
            self.week_grid.addWidget(header, 0, i + 1)
        
        # Crear diccionario para organizar eventos por día y hora
        week_events = {}
        for day in range(7):
            week_events[day] = {}
            for hour in range(24):
                week_events[day][hour] = []
        
        # Filtrar y organizar eventos de la semana
        week_start_date = datetime(
            week_start.year(),
            week_start.month(),
            week_start.day(),
            tzinfo=timezone.utc
        )
        week_end_date = week_start_date + timedelta(days=7)
        
        for event in self.events:
            if event.start_datetime < week_end_date and event.end_datetime >= week_start_date:
                event_start = event.start_datetime
                event_day = (event_start - week_start_date).days
                if 0 <= event_day <= 6:
                    event_hour = event_start.hour
                    week_events[event_day][event_hour].append(event)
        
        # Agregar horas y eventos
        for hour in range(24):
            # Etiqueta de hora
            hour_label = QLabel(f"{hour:02d}:00")
            hour_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            hour_label.setStyleSheet(Theme.HOUR_LABEL_STYLE)
            hour_label.setFixedWidth(60)
            self.week_grid.addWidget(hour_label, hour + 1, 0)
            
            # Agregar contenedores de eventos para cada día
            for day in range(7):
                cell = QWidget()
                cell_layout = QVBoxLayout(cell)
                cell_layout.setSpacing(2)
                cell_layout.setContentsMargins(2, 2, 2, 2)
                
                # Agregar eventos de esta hora
                events = week_events[day][hour]
                if events:
                    for event in events:
                        event_widget = EventLabel(event)
                        event_widget.setStyleSheet(Theme.EVENT_WEEK_STYLE)
                        cell_layout.addWidget(event_widget)
                
                cell.setStyleSheet(Theme.WEEK_CELL_STYLE)
                self.week_grid.addWidget(cell, hour + 1, day + 1)
        
        scroll.setWidget(scroll_widget)
        week_layout.addWidget(scroll)
        
        # Actualizar el contenedor de la semana
        if self.week_container.layout():
            old_layout = self.week_container.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(old_layout)
        
        self.week_container.setLayout(week_layout)
        self.view_stack.setCurrentWidget(self.week_container)

    def refresh_day_view(self):
        """Refresca la vista de día"""
        self._update_header()
        
        # Crear nuevo widget para la vista diaria
        day_widget = QWidget()
        day_layout = QVBoxLayout(day_widget)
        day_layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        
        main_layout = QGridLayout(scroll_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Filtrar eventos del día
        day_start = datetime(
            self.current_date.year(),
            self.current_date.month(),
            self.current_date.day(),
            tzinfo=timezone.utc
        )
        day_end = day_start + timedelta(days=1)
        
        # Separar eventos por tipo
        all_day_events = []
        timed_events = {}
        
        for event in self.events:
            if event.start_datetime < day_end and event.end_datetime >= day_start:
                if (event.start_datetime.hour == 0 and 
                    event.end_datetime.hour == 23 and 
                    event.end_datetime.minute == 59):
                    all_day_events.append(event)
                else:
                    start_time = event.start_datetime.strftime("%H:%M")
                    if start_time not in timed_events:
                        timed_events[start_time] = []
                    timed_events[start_time].append(event)
        
        # Sección de eventos de todo el día
        if all_day_events:
            all_day_container = QWidget()
            all_day_layout = QVBoxLayout(all_day_container)
            all_day_layout.setSpacing(2)
            all_day_layout.setContentsMargins(10, 5, 10, 5)
            
            all_day_header = QLabel("Todo el día")
            all_day_header.setStyleSheet(Theme.SECTION_HEADER_STYLE)
            all_day_layout.addWidget(all_day_header)
            
            for event in sorted(all_day_events, key=lambda e: e.title):
                event_widget = EventLabel(event)
                event_widget.setStyleSheet(Theme.EVENT_ALL_DAY_STYLE)
                all_day_layout.addWidget(event_widget)
            
            main_layout.addWidget(all_day_container, 0, 1)
            main_layout.addWidget(QLabel(), 0, 2)  # Espaciador
        
        # Columna de horas
        for hour in range(24):
            hour_label = QLabel(f"{hour:02d}:00")
            hour_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
            hour_label.setStyleSheet(Theme.HOUR_LABEL_STYLE)
            hour_label.setFixedWidth(60)
            main_layout.addWidget(hour_label, hour + 1, 0)
            
            # Contenedor para eventos de esta hora
            hour_container = QWidget()
            hour_layout = QVBoxLayout(hour_container)
            hour_layout.setSpacing(2)
            hour_layout.setContentsMargins(2, 0, 2, 0)
            
            # Agregar eventos de esta hora
            hour_str = f"{hour:02d}:"
            hour_events = []
            for time, events in timed_events.items():
                if time.startswith(hour_str):
                    hour_events.extend(events)
            
            if hour_events:
                for event in sorted(hour_events, key=lambda e: e.start_datetime):
                    event_widget = EventLabel(event)
                    event_widget.setStyleSheet(Theme.EVENT_TIMED_STYLE)
                    hour_layout.addWidget(event_widget)
            
            hour_container.setStyleSheet(Theme.HOUR_CELL_STYLE)
            main_layout.addWidget(hour_container, hour + 1, 1, 1, 2)
        
        scroll.setWidget(scroll_widget)
        day_layout.addWidget(scroll)
        
        # Actualizar el contenedor del día
        if self.day_container.layout():
            old_layout = self.day_container.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            QWidget().setLayout(old_layout)
        
        self.day_container.setLayout(day_layout)
        self.view_stack.setCurrentWidget(self.day_container)

    def change_view(self, view_text: str):
        """Cambia entre las diferentes vistas"""
        view_map = {'Mes': 'month', 'Semana': 'week', 'Día': 'day'}
        self.current_view = view_map[view_text]
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
        """Manejar cambios en la configuración"""
        self.update_auto_refresh()
        self.refresh_view()

    def clear_events(self):
        """Limpia todos los eventos del calendario"""
        self.events = []
        self.update_calendar()  # Actualizar vista 