from PyQt6.QtCore import QObject, pyqtSignal
from core.ai_assistant import AIAssistant

class Worker(QObject):
    finished = pyqtSignal(str)  # Señal para enviar la respuesta de vuelta
    error = pyqtSignal(str)      # Señal para enviar errores

    def __init__(self, ai_assistant: AIAssistant, message: str):
        super().__init__()
        self.ai_assistant = ai_assistant
        self.message = message

    def run(self):
        """Método que se ejecuta en el hilo separado"""
        try:
            response = self.ai_assistant.process_message(self.message)
            self.finished.emit(response)  # Emitir la respuesta
        except Exception as e:
            self.error.emit(str(e))  # Emitir el error 