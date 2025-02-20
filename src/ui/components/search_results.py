from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

class SearchResultItem(QFrame):
    clicked = pyqtSignal(object)  # Emite la lista de eventos

    def __init__(self, result, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                margin: 5px;
            }
            QFrame:hover {
                background: #f5f5f5;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Título y conteo
        title = QLabel(f"{result['title']} ({result['count']} ocurrencias)")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)
        
        # Descripción si existe
        if result['description']:
            desc = QLabel(result['description'])
            desc.setWordWrap(True)
            layout.addWidget(desc)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.result = result

    def mousePressEvent(self, event):
        self.clicked.emit(self.result['events'])

class SearchResultsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.hide()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 10)
        
        # Área scrolleable para resultados
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        scroll.setWidget(self.results_container)
        
        layout.addWidget(scroll)

    def update_results(self, results):
        """Actualiza la lista de resultados"""
        # Limpiar resultados anteriores
        for i in reversed(range(self.results_layout.count())):
            self.results_layout.itemAt(i).widget().deleteLater()
        
        if not results:
            label = QLabel("No se encontraron resultados")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_layout.addWidget(label)
        else:
            for result in results:
                item = SearchResultItem(result)
                item.clicked.connect(self.parent().calendar_widget.highlight_events)
                self.results_layout.addWidget(item)
        
        self.show() 