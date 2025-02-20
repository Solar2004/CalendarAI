from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from ..styles.theme import Theme

class AIToolbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Botón para optimizar horario
        optimize_btn = QPushButton("🔄 Optimizar Horario")
        optimize_btn.setToolTip("Reorganizar eventos para optimizar el tiempo")
        
        # Botón para sugerir huecos libres
        suggest_btn = QPushButton("⭐ Sugerir Espacios")
        suggest_btn.setToolTip("Encontrar mejores momentos para nuevos eventos")
        
        # Botón para análisis de productividad
        analytics_btn = QPushButton("📊 Análisis")
        analytics_btn.setToolTip("Ver análisis de uso del tiempo")
        
        # Botón para rutinas inteligentes
        routines_btn = QPushButton("🔄 Rutinas")
        routines_btn.setToolTip("Crear y gestionar rutinas automáticas")
        
        for btn in [optimize_btn, suggest_btn, analytics_btn, routines_btn]:
            btn.setStyleSheet(Theme.AI_BUTTON_STYLE)
            layout.addWidget(btn) 