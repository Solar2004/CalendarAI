from PyQt6.QtWidgets import QWidget, QVBoxLayout
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
        self.init_ui()

        # Timer para actualizar datos
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(1000)

    def init_ui(self):
        layout = QVBoxLayout(self)
        
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
        layout.addWidget(chart_view)

    def update_data(self):
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.Process().memory_percent()
        
        # Actualizar series
        self.cpu_series.append(QPointF(self.cpu_series.count(), cpu_usage))
        self.memory_series.append(QPointF(self.memory_series.count(), memory_usage))

        # Limitar el número de puntos en el gráfico
        if self.cpu_series.count() > 60:
            self.cpu_series.remove(0)
            self.memory_series.remove(0) 