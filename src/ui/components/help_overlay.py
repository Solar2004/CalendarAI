from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint, QSize, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QPen, QLinearGradient

class RunicHelpOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Widget)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setup_ui()
        self.hide()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(50, 50, 50, 50)
        
        self.content = QLabel()
        self.content.setWordWrap(True)
        self.content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content.setStyleSheet("""
            QLabel {
                color: #E8D5B5;
                font-size: 16px;
                padding: 20px;
                background: transparent;
            }
        """)
        
        self.layout.addWidget(self.content)

    def show_help(self, text: str, parent_size: QSize, button_pos: QPoint):
        self.content.setText(text)
        self.resize(parent_size)
        self.show()
        self.raise_()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Fondo semi-transparente
        painter.fillRect(self.rect(), QColor(0, 0, 0, 180))

        # Crear el marco rúnico
        rect = self.rect()
        center_rect = QRectF(
            rect.width()//4,
            rect.height()//4,
            rect.width()//2,
            rect.height()//2
        )

        # Gradiente para el fondo del marco
        gradient = QLinearGradient(
            center_rect.topLeft(),
            center_rect.bottomRight()
        )
        gradient.setColorAt(0, QColor(40, 30, 20))
        gradient.setColorAt(1, QColor(70, 50, 30))

        # Dibujar el fondo del marco
        path = QPainterPath()
        path.addRoundedRect(center_rect, 15.0, 15.0)
        painter.fillPath(path, gradient)

        # Dibujar bordes rúnicos
        pen = QPen(QColor("#C0A080"))
        pen.setWidth(3)
        painter.setPen(pen)

        # Dibujar símbolos rúnicos en las esquinas
        margin = 20.0
        size = 30.0
        for corner in ['TL', 'TR', 'BL', 'BR']:
            if corner == 'TL':
                x = center_rect.left() + margin
                y = center_rect.top() + margin
            elif corner == 'TR':
                x = center_rect.right() - margin - size
                y = center_rect.top() + margin
            elif corner == 'BL':
                x = center_rect.left() + margin
                y = center_rect.bottom() - margin - size
            else:  # BR
                x = center_rect.right() - margin - size
                y = center_rect.bottom() - margin - size

            # Dibujar símbolo rúnico
            self._draw_rune(painter, x, y, size)

        # Dibujar el borde principal
        painter.drawRoundedRect(center_rect, 15.0, 15.0)

    def _draw_rune(self, painter: QPainter, x: float, y: float, size: float):
        """Dibuja un símbolo rúnico decorativo"""
        pen = painter.pen()
        pen.setWidth(2)
        painter.setPen(pen)
        
        # Dibujar una runa simple usando valores float
        painter.drawLine(
            QPointF(x, y),
            QPointF(x + size/2, y + size)
        )
        painter.drawLine(
            QPointF(x + size/2, y + size),
            QPointF(x + size, y)
        )
        painter.drawLine(
            QPointF(x + size/2, y),
            QPointF(x + size/2, y + size)
        ) 