from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGridLayout, QFrame, QComboBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon
import calendar
import os

class MiniCalendar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_date = QDate.currentDate()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header con mes y año actual
        self.month_header = QWidget()
        month_header_layout = QHBoxLayout(self.month_header)
        month_header_layout.setContentsMargins(5, 5, 5, 5)

        # Botones de navegación
        prev_month = QPushButton()
        prev_month_icon = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'arrow_left.svg')
        prev_month.setIcon(QIcon(prev_month_icon))
        prev_month.clicked.connect(self.previous_month)
        prev_month.setFixedSize(24, 24)
        prev_month.setStyleSheet("background: transparent; border: none;")

        self.month_label = QLabel(self.current_date.toString("MMMM yyyy"))
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.month_label.setStyleSheet("font-weight: bold; color: #1a73e8;")

        next_month = QPushButton()
        next_month_icon = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'arrow_right.svg')
        next_month.setIcon(QIcon(next_month_icon))
        next_month.clicked.connect(self.next_month)
        next_month.setFixedSize(24, 24)
        next_month.setStyleSheet("background: transparent; border: none;")

        month_header_layout.addWidget(prev_month)
        month_header_layout.addWidget(self.month_label, stretch=1)
        month_header_layout.addWidget(next_month)

        layout.addWidget(self.month_header)

        # Días de la semana
        days_widget = QWidget()
        days_layout = QGridLayout(days_widget)
        days_layout.setSpacing(0)
        days = ['D', 'L', 'M', 'M', 'J', 'V', 'S']
        
        for i, day in enumerate(days):
            label = QLabel(day)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("""
                color: #5f6368;
                font-size: 12px;
                padding: 5px;
            """)
            days_layout.addWidget(label, 0, i)

        layout.addWidget(days_widget)

        # Grid del calendario
        self.calendar_grid = QGridLayout()
        self.calendar_grid.setSpacing(0)
        layout.addLayout(self.calendar_grid)
        
        self.update_calendar()

        # Estilo general
        self.setStyleSheet("""
            MiniCalendar {
                background: white;
                border: 1px solid #dadce0;
                border-radius: 8px;
            }
        """)

    def update_calendar(self):
        # Limpiar grid existente
        while self.calendar_grid.count():
            item = self.calendar_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Obtener el calendario del mes actual
        year = self.current_date.year()
        month = self.current_date.month()
        cal = calendar.monthcalendar(year, month)

        today = QDate.currentDate()
        
        # Llenar el calendario
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day != 0:
                    day_widget = QFrame()
                    day_widget.setFixedSize(24, 24)
                    day_layout = QVBoxLayout(day_widget)
                    day_layout.setContentsMargins(0, 0, 0, 0)
                    
                    day_label = QLabel(str(day))
                    day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    # Estilo para el día actual
                    if (day == today.day() and 
                        month == today.month() and 
                        year == today.year()):
                        day_widget.setStyleSheet("""
                            QFrame {
                                background: #1a73e8;
                                border-radius: 12px;
                            }
                            QLabel {
                                color: white;
                                font-weight: bold;
                            }
                        """)
                    else:
                        day_widget.setStyleSheet("""
                            QFrame:hover {
                                background: #f1f3f4;
                                border-radius: 12px;
                            }
                            QLabel {
                                color: #3c4043;
                            }
                        """)
                    
                    day_layout.addWidget(day_label)
                    self.calendar_grid.addWidget(day_widget, week_num, day_num)

    def previous_month(self):
        self.current_date = self.current_date.addMonths(-1)
        self.month_label.setText(self.current_date.toString("MMMM yyyy"))
        self.update_calendar()

    def next_month(self):
        self.current_date = self.current_date.addMonths(1)
        self.month_label.setText(self.current_date.toString("MMMM yyyy"))
        self.update_calendar() 