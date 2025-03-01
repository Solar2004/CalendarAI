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
from ..styles.theme import Theme

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
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setBackgroundBrush(QColor("#ffffff"))
        
        layout.addWidget(self.chart_view)
        
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
        
    def update_theme(self):
        """Actualiza los estilos cuando cambia el tema"""
        is_dark = Theme.is_dark_mode
        bg_color = Theme.DARK_BG if is_dark else Theme.LIGHT_BG
        text_color = Theme.DARK_TEXT if is_dark else Theme.LIGHT_TEXT
        grid_color = Theme.DARK_BORDER if is_dark else "#e0e0e0"
        
        # Actualizar colores del gráfico
        self.chart.setBackgroundBrush(QColor(bg_color))
        self.chart.setTitleBrush(QColor(text_color))
        self.chart_view.setBackgroundBrush(QColor(bg_color))
        
        # Actualizar colores de los ejes
        self.axis_x.setLabelsColor(QColor(text_color))
        self.axis_x.setTitleBrush(QColor(text_color))
        self.axis_x.setGridLineColor(QColor(grid_color))
        
        self.axis_y.setLabelsColor(QColor(text_color))
        self.axis_y.setTitleBrush(QColor(text_color))
        self.axis_y.setGridLineColor(QColor(grid_color))

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
        if self.log_handler and self.log_handler in logging.getLogger().handlers:
            logging.getLogger().removeHandler(self.log_handler)
        super().closeEvent(event)

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.reload_button = QPushButton("Recargar Logs")
        self.reload_button.clicked.connect(self.load_existing_logs)
        
        self.clear_button = QPushButton("Limpiar")
        self.clear_button.clicked.connect(self.log_text.clear)
        
        toolbar.addWidget(self.reload_button)
        toolbar.addWidget(self.clear_button)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # Agregar el log viewer que ya fue creado
        layout.addWidget(self.log_text)

    def load_existing_logs(self):
        """Carga los logs existentes desde el archivo"""
        try:
            # Obtener el archivo de log actual
            current_date = datetime.now().strftime("%Y%m%d")
            log_file = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'logs', f"calendar_app_{current_date}.log")
            app_log = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'app.log')
            
            # Intentar primero el log específico del día, luego el log general
            log_files = [log_file, app_log]
            
            for file_path in log_files:
                if os.path.exists(file_path):
                    # Intentar diferentes codificaciones
                    encodings = ['utf-8', 'latin1', 'cp1252']
                    
                    for encoding in encodings:
                        try:
                            with open(file_path, 'r', encoding=encoding) as f:
                                # Leer las últimas 1000 líneas
                                lines = f.readlines()[-1000:]
                                self.log_text.setPlainText(''.join(lines))
                                # Mover el cursor al final
                                self.log_text.moveCursor(QTextCursor.MoveOperation.End)
                                logger.info(f"Logs cargados exitosamente desde {file_path} usando codificación {encoding}")
                                return
                        except UnicodeDecodeError:
                            continue
                        except Exception as e:
                            logger.error(f"Error leyendo logs con codificación {encoding}: {e}")
                            continue
            
            logger.error("No se encontraron archivos de log o no se pudieron leer")
        except Exception as e:
            logger.error(f"Error cargando logs existentes: {e}")

    def setup_log_handler(self):
        class QTextEditLogger(logging.Handler):
            def __init__(self, widget):
                super().__init__()
                self.widget = widget
                self.setLevel(logging.INFO)  # Capturar todos los niveles de log

            def emit(self, record):
                try:
                    msg = self.format(record)
                    self.widget.appendPlainText(msg)
                    self.widget.moveCursor(QTextCursor.MoveOperation.End)
                except (RuntimeError, AttributeError):
                    # Widget fue destruido o no es accesible
                    pass

        # Remover handler anterior si existe
        if self.log_handler and self.log_handler in logging.getLogger().handlers:
            logging.getLogger().removeHandler(self.log_handler)

        # Crear y configurar el nuevo handler
        self.log_handler = QTextEditLogger(self.log_text)
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Agregar el handler al logger raíz para capturar todos los logs
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)
        
    def update_theme(self):
        """Actualiza los estilos cuando cambia el tema"""
        is_dark = Theme.is_dark_mode
        bg_color = Theme.DARK_BG if is_dark else Theme.LIGHT_BG
        text_color = Theme.DARK_TEXT if is_dark else Theme.LIGHT_TEXT
        border_color = Theme.DARK_BORDER if is_dark else Theme.LIGHT_BORDER
        
        # Actualizar estilos de los botones
        button_style = Theme.PRIMARY_BUTTON_STYLE if is_dark else Theme.PRIMARY_BUTTON_STYLE_LIGHT
        self.reload_button.setStyleSheet(button_style)
        self.clear_button.setStyleSheet(button_style)
        
        # Actualizar estilo del visor de logs
        self.log_text.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 4px;
                font-family: monospace;
            }}
        """)

class DevPanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        self.main_window = parent
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        self.setWindowTitle("Panel de Desarrollo")
        self.resize(800, 600)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Crear pestañas
        self.tabs = QTabWidget()
        
        # Pestaña de rendimiento
        performance_tab = QWidget()
        performance_layout = QVBoxLayout(performance_tab)
        self.performance_graph = PerformanceGraph()
        performance_layout.addWidget(self.performance_graph)
        
        # Pestaña de logs
        logs_tab = QWidget()
        logs_layout = QVBoxLayout(logs_tab)
        self.log_viewer = LogViewer()
        logs_layout.addWidget(self.log_viewer)
        
        # Pestaña de configuración
        config_tab = QWidget()
        config_layout = QVBoxLayout(config_tab)
        
        # Secciones de configuración
        api_section = self._create_api_section()
        refresh_section = self._create_refresh_section()
        
        config_layout.addWidget(api_section)
        config_layout.addWidget(refresh_section)
        config_layout.addStretch()
        
        # Agregar pestañas
        self.tabs.addTab(performance_tab, "Rendimiento")
        self.tabs.addTab(logs_tab, "Logs")
        self.tabs.addTab(config_tab, "Configuración")
        
        main_layout.addWidget(self.tabs)
        
        # Botones de acción (sin botón de cerrar)
        button_section = self._create_button_section()
        main_layout.addWidget(button_section)

    def _create_main_layout(self):
        """Crea el layout principal con pestañas"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Crear pestañas
        tabs = QTabWidget()
        
        # Pestaña de rendimiento
        performance_tab = QWidget()
        performance_layout = QVBoxLayout(performance_tab)
        performance_graph = PerformanceGraph()
        performance_layout.addWidget(performance_graph)
        
        # Pestaña de logs
        logs_tab = QWidget()
        logs_layout = QVBoxLayout(logs_tab)
        log_viewer = LogViewer()
        logs_layout.addWidget(log_viewer)
        
        # Agregar pestañas
        tabs.addTab(performance_tab, "Rendimiento")
        tabs.addTab(logs_tab, "Logs")
        
        layout.addWidget(tabs)
        
        return container

    def _create_api_section(self):
        """Crea la sección de configuración de API"""
        section = QFrame()
        section.setFrameShape(QFrame.Shape.StyledPanel)
        
        layout = QVBoxLayout(section)
        
        # Título
        title = QLabel("Configuración de API")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Checkbox para usar API mock
        self.use_mock_api = QCheckBox("Usar API Mock")
        self.use_mock_api.setChecked(self.settings.use_mock_api)
        
        # Campo de texto para la respuesta mock
        mock_response_label = QLabel("Respuesta Mock API:")
        self.mock_api_response = QTextEdit()
        self.mock_api_response.setPlainText(self.settings.mock_api_response)
        self.mock_api_response.setMinimumHeight(100)
        
        layout.addWidget(title)
        layout.addWidget(self.use_mock_api)
        layout.addWidget(mock_response_label)
        layout.addWidget(self.mock_api_response)
        
        return section

    def _create_refresh_section(self):
        """Crea la sección de configuración de refresco automático"""
        section = QFrame()
        section.setFrameShape(QFrame.Shape.StyledPanel)
        
        layout = QVBoxLayout(section)
        
        # Título
        title = QLabel("Configuración de Refresco")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Checkbox para auto-refresh
        self.auto_refresh = QCheckBox("Habilitar refresco automático")
        self.auto_refresh.setChecked(self.settings.auto_refresh_enabled)
        
        # Botones para guardar cambios
        button_layout = QHBoxLayout()
        save_button = QPushButton("Guardar Cambios")
        save_button.clicked.connect(self.save_settings)
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        
        layout.addWidget(title)
        layout.addWidget(self.auto_refresh)
        layout.addLayout(button_layout)
        
        return section

    def _create_button_section(self):
        """Crea la sección de botones de acción"""
        section = QFrame()
        
        layout = QHBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Botón para guardar configuración
        save_button = QPushButton("Guardar Configuración")
        save_button.clicked.connect(self.save_settings)
        
        # Agregar botones al layout
        layout.addStretch()
        layout.addWidget(save_button)
        
        return section

    def save_settings(self):
        """Guarda la configuración actual"""
        try:
            # Actualizar configuración
            self.settings.use_mock_api = self.use_mock_api.isChecked()
            self.settings.auto_refresh_enabled = self.auto_refresh.isChecked()
            self.settings.mock_api_response = self.mock_api_response.toPlainText()
            
            # Guardar configuración
            self.settings.save()
            
            # Notificar al usuario
            logger.info("Configuración guardada exitosamente")
            
            # Actualizar componentes que dependen de la configuración
            if self.main_window:
                self.main_window.on_settings_changed()
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            
    def apply_theme(self):
        """Aplica estilos basados en el tema actual"""
        is_dark = Theme.is_dark_mode
        bg_color = Theme.DARK_BG if is_dark else Theme.LIGHT_BG
        text_color = Theme.DARK_TEXT if is_dark else Theme.LIGHT_TEXT
        border_color = Theme.DARK_BORDER if is_dark else Theme.LIGHT_BORDER
        secondary_text = Theme.DARK_SECONDARY_TEXT if is_dark else Theme.LIGHT_SECONDARY_TEXT
        
        # Estilo para el diálogo
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                color: {text_color};
            }}
            QTabWidget::pane {{
                border: 1px solid {border_color};
                border-radius: 4px;
                background-color: {bg_color};
            }}
            QTabBar::tab {{
                background-color: {Theme.DARK_HOVER if is_dark else "#f0f0f0"};
                border: 1px solid {border_color};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                color: {text_color};
            }}
            QTabBar::tab:selected {{
                background-color: {bg_color};
                border-bottom-color: {bg_color};
            }}
            QCheckBox {{
                spacing: 8px;
                color: {text_color};
            }}
            QLabel {{
                color: {text_color};
            }}
            QFrame {{
                background-color: {Theme.DARK_HOVER if is_dark else "#f8f9fa"};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 12px;
            }}
        """)
        
        # Actualizar componentes que tienen método update_theme
        if hasattr(self, 'performance_graph') and hasattr(self.performance_graph, 'update_theme'):
            self.performance_graph.update_theme()
            
        if hasattr(self, 'log_viewer') and hasattr(self.log_viewer, 'update_theme'):
            self.log_viewer.update_theme()
            
    def update_theme(self):
        """Actualiza los estilos cuando cambia el tema"""
        self.apply_theme() 