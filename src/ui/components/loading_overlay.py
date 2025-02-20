from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QPen, QLinearGradient
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GenericOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Guardar el evento original de resize del padre
        if parent:
            self._parent_original_resize = parent.resizeEvent
            parent.resizeEvent = self._handle_parent_resize
        self.setup_ui()
        self.hide()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_label.setStyleSheet("""
            QLabel {
                color: #E8D5B5;
                font-size: 16px;
                padding: 20px;
                background: transparent;
            }
        """)
        
        layout.addStretch()
        layout.addWidget(self.content_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
        # Estilo base del overlay
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 180);
            }
        """)
        
    def _handle_parent_resize(self, event):
        """Maneja el redimensionamiento del padre sin causar recursión"""
        try:
            # Verificar que el widget aún es válido
            if not self.parent() or not self.isVisible():
                return
                
            # Llamar al evento original
            if hasattr(self, '_parent_original_resize'):
                self._parent_original_resize(event)
                
            # Ajustar nuestro tamaño
            self.resize(self.parent().size())
            
        except RuntimeError:
            # Si el widget fue eliminado, no hacer nada
            pass
        
    def show_message(self, text: str, style="default"):
        """Muestra un mensaje con un estilo específico"""
        self.content_label.setText(text)
        
        if style == "runic":
            self.setStyleSheet("""
                QWidget {
                    background-color: rgba(0, 0, 0, 180);
                }
                QLabel {
                    color: white;
                    font-size: 16px;
                    padding: 20px;
                    margin: 20px;
                    background-color: rgba(0, 0, 0, 220);
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: rgba(0, 0, 0, 180);
                }
                QLabel {
                    color: white;
                    font-size: 16px;
                    padding: 20px;
                }
            """)
            
        self.show()
        self.raise_()
        
    def hide_message(self):
        """Oculta el overlay"""
        self.hide()

class LoadingOverlay(GenericOverlay):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        
        # Crear layout para status y tiempo
        self.status_layout = QVBoxLayout()
        self.status_label = QLabel()
        self.time_label = QLabel("Tiempo: 0s")
        
        # Estilos
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                margin-bottom: 10px;
            }
        """)
        self.time_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-style: italic;
            }
        """)
        
        # Agregar labels al layout
        self.status_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.status_layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Reemplazar el contenido del layout principal
        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addLayout(self.status_layout)
        layout.addStretch()
        
    def start(self, initial_status="Iniciando análisis..."):
        self.show()
        self.status_label.setText(initial_status)
        self.start_time = datetime.now()
        self.timer.start(1000)
        
    def update_status(self, status: str):
        self.status_label.setText(status)
        
    def update_time(self):
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).seconds
            self.time_label.setText(f"Tiempo: {elapsed}s")
            
    def stop(self):
        """Detiene y oculta el overlay"""
        try:
            # Detener timer
            if self.timer:
                self.timer.stop()
            
            # Desconectar eventos de resize
            if self.parent():
                self.parent().resizeEvent = self._parent_original_resize
            
            # Limpiar y ocultar
            self.hide()
            self.status_label.clear()
            self.time_label.clear()
            
            # Desconectar del padre y programar para eliminación
            self.setParent(None)
            self.deleteLater()
            
        except Exception as e:
            logger.error(f"Error deteniendo overlay: {e}")

    def _handle_parent_resize(self, event):
        """Maneja el redimensionamiento del padre sin causar recursión"""
        try:
            # Verificar que el widget aún es válido
            if not self.parent() or not self.isVisible():
                return
                
            # Llamar al evento original
            if hasattr(self, '_parent_original_resize'):
                self._parent_original_resize(event)
                
            # Ajustar nuestro tamaño
            self.resize(self.parent().size())
            
        except RuntimeError:
            # Si el widget fue eliminado, no hacer nada
            pass 