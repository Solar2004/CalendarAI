from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt

class NotificationCenter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notifications = []
        
    def show_notification(self, title, message, type="info"):
        notification = NotificationWidget(title, message, type)
        self.notifications.append(notification)
        # Mostrar notificación con animación 