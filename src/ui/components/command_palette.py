from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem

class CommandPalette(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Comandos Rápidos")
        layout = QVBoxLayout(self)
        
        # Barra de búsqueda con autocompletado
        self.search = QLineEdit()
        self.search.setPlaceholderText("Escribe un comando o pregunta...")
        
        # Lista de comandos comunes
        self.commands = [
            "Crear evento recurrente",
            "Encontrar tiempo libre",
            "Optimizar agenda de hoy",
            "Analizar patrones de tiempo",
            "Sugerir mejor hora para reunión",
            "Generar reporte semanal"
        ]
        
        self.command_list = QListWidget()
        self.command_list.addItems(self.commands)
        
        layout.addWidget(self.search)
        layout.addWidget(self.command_list)
        
        self.setLayout(layout) 