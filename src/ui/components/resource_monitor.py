from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PyQt6.QtCore import QTimer, QPointF, Qt
import psutil
from PyQt6.QtGui import QPainter, QColor, QFont

class ResourceMonitor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(300)
        self.cpu_series = QLineSeries()
        self.memory_series = QLineSeries()
        self.is_monitoring = True
        self.init_ui()

        # Timer para actualizar datos
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(1000)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Crear chart
        self.chart = QChart()
        self.chart.setTitle("Monitoreo de Recursos")
        self.chart.setTitleFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart.setBackgroundBrush(QColor("#ffffff"))

        # Configurar series
        self.cpu_series.setName("CPU")
        self.memory_series.setName("Memoria")

        self.chart.addSeries(self.cpu_series)
        self.chart.addSeries(self.memory_series)

        # Configurar ejes
        self.axis_x = QValueAxis()
        self.axis_x.setRange(0, 60)
        self.axis_x.setLabelFormat("%d s")
        self.axis_x.setTitleText("Tiempo (segundos)")
        
        self.axis_y = QValueAxis()
        self.axis_y.setRange(0, 100)
        self.axis_y.setLabelFormat("%.1f%%")
        self.axis_y.setTitleText("Utilización")

        self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)

        self.cpu_series.attachAxis(self.axis_x)
        self.cpu_series.attachAxis(self.axis_y)
        self.memory_series.attachAxis(self.axis_x)
        self.memory_series.attachAxis(self.axis_y)

        # Crear chart view
        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        main_layout.addWidget(chart_view)

        # Añadir botones de control
        buttons_layout = QHBoxLayout()
        
        self.pause_button = QPushButton("Pausar")
        self.pause_button.clicked.connect(self.toggle_monitoring)
        
        self.reset_button = QPushButton("Reiniciar")
        self.reset_button.clicked.connect(self.reset_monitoring)
        
        buttons_layout.addWidget(self.pause_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)

    def toggle_monitoring(self):
        self.is_monitoring = not self.is_monitoring
        if self.is_monitoring:
            self.pause_button.setText("Pausar")
            self.update_timer.start()
        else:
            self.pause_button.setText("Reanudar")
            self.update_timer.stop()

    def reset_monitoring(self):
        # Limpiar datos
        self.cpu_series.clear()
        self.memory_series.clear()
        # Resetear el rango del eje X
        self.axis_x.setRange(0, 60)
        # Asegurar que el monitoreo está activo
        self.is_monitoring = True
        self.pause_button.setText("Pausar")
        self.update_timer.start()

    def update_data(self):
        if not self.is_monitoring:
            return
            
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.Process().memory_percent()
        
        current_time = self.cpu_series.count()
        
        # Actualizar series
        self.cpu_series.append(QPointF(current_time, cpu_usage))
        self.memory_series.append(QPointF(current_time, memory_usage))

        # Actualizar el rango del eje X para crear efecto de desplazamiento
        if current_time > 60:
            self.axis_x.setRange(current_time - 60, current_time)
            
            # Mantener solo los últimos 300 puntos para evitar uso excesivo de memoria
            while self.cpu_series.count() > 300:
                self.cpu_series.remove(0)
                self.memory_series.remove(0) 