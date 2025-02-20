from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QCheckBox, QLabel, QTextEdit, QPushButton,
    QTabWidget, QWidget, QPlainTextEdit,
    QFrame, QSplitter
)
from PyQt6.QtCore import QTimer, QPointF, Qt
from PyQt6.QtGui import (
    QPainter, QPen, QColor,
    QTextCursor, QFont
)
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
import psutil
import threading
import logging
from utils.logger import logger
from config.settings import Settings
import os
from datetime import datetime

class PerformanceGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(300)
        self.cpu_history = []
        self.memory_history = []
        self.thread_usage = {}
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Crear chart con estilo moderno
        self.chart = QChart()
        self.chart.setTitle("Monitoreo de Rendimiento")
        self.chart.setTitleFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart.setBackgroundBrush(QColor("#ffffff"))
        self.chart.legend().setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Series con colores modernos
        self.cpu_series = QLineSeries()
        self.cpu_series.setName("CPU")
        self.cpu_series.setColor(QColor("#2196F3"))  # Material Blue
        
        self.memory_series = QLineSeries()
        self.memory_series.setName("Memoria")
        self.memory_series.setColor(QColor("#4CAF50"))  # Material Green
        
        # Ejes con mejor formato
        self.axis_x = QValueAxis()
        self.axis_x.setRange(0, 60)
        self.axis_x.setLabelFormat("%d s")
        self.axis_x.setTitleText("Tiempo (segundos)")
        self.axis_x.setTitleFont(QFont("Segoe UI", 10))
        self.axis_x.setLabelsFont(QFont("Segoe UI", 9))
        self.axis_x.setGridLineColor(QColor("#e0e0e0"))
        
        self.axis_y = QValueAxis()
        self.axis_y.setRange(0, 100)
        self.axis_y.setLabelFormat("%.1f%%")
        self.axis_y.setTitleText("Utilización")
        self.axis_y.setTitleFont(QFont("Segoe UI", 10))
        self.axis_y.setLabelsFont(QFont("Segoe UI", 9))
        self.axis_y.setGridLineColor(QColor("#e0e0e0"))
        
        self.chart.addSeries(self.cpu_series)
        self.chart.addSeries(self.memory_series)
        self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        
        self.cpu_series.attachAxis(self.axis_x)
        self.cpu_series.attachAxis(self.axis_y)
        self.memory_series.attachAxis(self.axis_x)
        self.memory_series.attachAxis(self.axis_y)
        
        # Crear chart view con fondo blanco
        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setBackgroundBrush(QColor("#ffffff"))
        
        layout.addWidget(chart_view)
        
        # Timer para actualizar datos
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(1000)
        
        self.time_counter = 0

    def update_data(self):
        self.time_counter += 1
        if self.time_counter > 60:
            self.time_counter = 0
            self.cpu_series.clear()
            self.memory_series.clear()
            
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.Process().memory_percent()
        
        self.cpu_series.append(QPointF(self.time_counter, cpu_usage))
        self.memory_series.append(QPointF(self.time_counter, memory_usage))

class LogViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumBlockCount(5000)
        self.log_handler = None  # Guardar referencia al handler
        self.init_ui()
        self.load_existing_logs()
        self.setup_log_handler()

    def closeEvent(self, event):
        """Limpiar el handler cuando se cierra el widget"""
        if self.log_handler and self.log_handler in logger.handlers:
            logger.removeHandler(self.log_handler)
        super().closeEvent(event)

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        reload_button = QPushButton("Recargar Logs")
        reload_button.clicked.connect(self.load_existing_logs)
        
        clear_button = QPushButton("Limpiar")
        clear_button.clicked.connect(self.log_text.clear)
        
        toolbar.addWidget(reload_button)
        toolbar.addWidget(clear_button)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # Agregar el log viewer que ya fue creado
        layout.addWidget(self.log_text)

    def load_existing_logs(self):
        """Carga los logs existentes desde el archivo"""
        try:
            # Obtener el archivo de log actual
            current_date = datetime.now().strftime("%Y%m%d")
            log_file = f"logs/calendar_app_{current_date}.log"
            
            if os.path.exists(log_file):
                # Intentar diferentes codificaciones
                encodings = ['utf-8', 'latin1', 'cp1252']
                
                for encoding in encodings:
                    try:
                        with open(log_file, 'r', encoding=encoding) as f:
                            # Leer las últimas 1000 líneas
                            lines = f.readlines()[-1000:]
                            self.log_text.setPlainText(''.join(lines))
                            # Mover el cursor al final
                            self.log_text.moveCursor(QTextCursor.MoveOperation.End)
                            logger.info(f"Logs cargados exitosamente usando codificación {encoding}")
                            break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        logger.error(f"Error leyendo logs con codificación {encoding}: {e}")
                        continue
                else:
                    logger.error("No se pudo leer el archivo de logs con ninguna codificación")
        except Exception as e:
            logger.error(f"Error cargando logs existentes: {e}")

    def setup_log_handler(self):
        class QTextEditLogger(logging.Handler):
            def __init__(self, widget):
                super().__init__()
                self.widget = widget

            def emit(self, record):
                try:
                    msg = self.format(record)
                    self.widget.appendPlainText(msg)
                    self.widget.moveCursor(QTextCursor.MoveOperation.End)
                except (RuntimeError, AttributeError):
                    # Widget fue destruido o no es accesible
                    logger.removeHandler(self)

        # Remover handler anterior si existe
        if self.log_handler in logger.handlers:
            logger.removeHandler(self.log_handler)

        self.log_handler = QTextEditLogger(self.log_text)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(self.log_handler)

class DevPanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.main_window = parent
        self.init_ui()
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton[text="Cancelar"] {
                background-color: #f44336;
            }
            QPushButton[text="Cancelar"]:hover {
                background-color: #d32f2f;
            }
            QCheckBox {
                spacing: 8px;
            }
            QTextEdit, QPlainTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 4px;
            }
            QLabel {
                color: #333;
                font-weight: bold;
            }
        """)

    def init_ui(self):
        self.setWindowTitle('Panel de Desarrollo')
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # TabWidget con estilo moderno
        tab_widget = QTabWidget()
        tab_widget.setDocumentMode(True)
        
        # Configuración
        config_tab = QWidget()
        config_layout = self._create_main_layout()
        config_tab.setLayout(config_layout)
        tab_widget.addTab(config_tab, "⚙️ Configuración")
        
        # Rendimiento
        performance_tab = QWidget()
        performance_layout = QVBoxLayout()
        performance_layout.setContentsMargins(10, 10, 10, 10)
        self.performance_graph = PerformanceGraph()
        performance_layout.addWidget(self.performance_graph)
        performance_tab.setLayout(performance_layout)
        tab_widget.addTab(performance_tab, "📊 Rendimiento")
        
        # Logs con splitter
        log_container = QWidget()
        log_layout = QVBoxLayout(log_container)
        log_layout.setContentsMargins(10, 10, 10, 10)
        
        splitter = QSplitter(Qt.Orientation.Vertical)
        self.log_viewer = LogViewer()
        splitter.addWidget(self.log_viewer)
        
        log_layout.addWidget(splitter)
        tab_widget.addTab(log_container, "📝 Logs")
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)

    def _create_main_layout(self):
        """Crea y retorna el layout principal con todos los widgets"""
        layout = QVBoxLayout()
        
        # API Settings
        layout.addLayout(self._create_api_section())
        
        # Auto Refresh Settings
        layout.addLayout(self._create_refresh_section())
        
        # Buttons
        layout.addLayout(self._create_button_section())
        
        return layout

    def _create_api_section(self):
        """Crea la sección de configuración de API"""
        api_layout = QVBoxLayout()
        
        # Mock API Toggle
        self.mock_api_checkbox = QCheckBox('Usar API Simulada')
        self.mock_api_checkbox.setChecked(self.settings.use_mock_api)
        api_layout.addWidget(self.mock_api_checkbox)
        
        # Mock Response Editor
        api_layout.addWidget(QLabel('Respuesta Simulada:'))
        self.response_editor = QTextEdit()
        self.response_editor.setPlainText(self.settings.mock_api_response)
        api_layout.addWidget(self.response_editor)
        
        return api_layout

    def _create_refresh_section(self):
        """Crea la sección de configuración de auto-refresh"""
        refresh_layout = QHBoxLayout()
        self.auto_refresh_checkbox = QCheckBox('Auto-Refresh Habilitado (20s)')
        self.auto_refresh_checkbox.setChecked(self.settings.auto_refresh_enabled)
        refresh_layout.addWidget(self.auto_refresh_checkbox)
        return refresh_layout

    def _create_button_section(self):
        """Crea la sección de botones"""
        button_layout = QHBoxLayout()
        
        save_button = QPushButton('Guardar')
        save_button.clicked.connect(self.save_settings)
        
        cancel_button = QPushButton('Cancelar')
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        return button_layout

    def save_settings(self):
        """Guarda los cambios en la configuración y actualiza el calendario"""
        # Actualizar settings
        self.settings.use_mock_api = self.mock_api_checkbox.isChecked()
        self.settings.mock_api_response = self.response_editor.toPlainText()
        self.settings.auto_refresh_enabled = self.auto_refresh_checkbox.isChecked()
        self.settings.save()
        
        # Actualizar calendario
        if hasattr(self.main_window, 'calendar_widget'):
            logger.info("Recargando configuración en CalendarWidget")
            self.main_window.calendar_widget.settings = self.settings
            self.main_window.calendar_widget.update_auto_refresh()
        
        self.accept() 