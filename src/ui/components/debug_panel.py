from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class DebugPanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Debug Panel")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)

        layout = QVBoxLayout(self)

        # Agregar contenido de prueba
        layout.addWidget(QLabel("Este es el panel de depuración."))

        # Botón de prueba
        test_button = QPushButton("Ejecutar Prueba")
        test_button.clicked.connect(self.run_test)
        layout.addWidget(test_button)

    def run_test(self):
        # Lógica de prueba aquí
        print("Prueba ejecutada.") 