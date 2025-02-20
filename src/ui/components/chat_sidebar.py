from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QScrollArea, QLabel, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint, QTimer
from PyQt6.QtGui import QIcon, QColor
from ..styles.theme import Theme
from core.ai_assistant import AIAssistant
from core.calendar_analyzer import CalendarAnalyzer
from .loading_overlay import LoadingOverlay
from .analysis_worker import AnalysisWorker
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatMessage(QWidget):
    def __init__(self, text: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        message = QLabel(text)
        message.setWordWrap(True)
        message.setStyleSheet(
            Theme.CHAT_MESSAGE_USER_STYLE if is_user 
            else Theme.CHAT_MESSAGE_AI_STYLE
        )
        
        # Agregar un poco de sombra para que se destaque del fondo
        message.setGraphicsEffect(QGraphicsDropShadowEffect(
            blurRadius=4,
            color=QColor(0, 0, 0, 25),
            offset=QPoint(0, 2)
        ))
        
        layout.addWidget(message)

class ChatSidebar(QWidget):
    messageSubmitted = pyqtSignal(str)

    def __init__(self, parent=None, db_manager=None, calendar_manager=None):
        super().__init__(parent)
        self.init_ui()
        self.message_history = []
        self.setStyleSheet(Theme.SIDEBAR_STYLE)
        self.ai_assistant = AIAssistant(db_manager)
        self.calendar_analyzer = CalendarAnalyzer(
            calendar_manager=calendar_manager,
            db_manager=db_manager
        )
        
        self.analysis_worker = None
        self.loading_overlay = None

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Área de mensajes
        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.addStretch()
        self.chat_area.setWidget(self.chat_widget)
        
        # Área de entrada
        input_area = QWidget()
        input_layout = QVBoxLayout(input_area)
        
        # Campo de texto con manejo de Enter
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Escribe un mensaje...")
        self.input_field.setMaximumHeight(100)
        self.input_field.setStyleSheet(Theme.CHAT_INPUT_STYLE)
        self.input_field.keyPressEvent = self.handle_input_key_press
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        # Botón de enviar
        self.send_button = QPushButton("Enviar")
        self.send_button.setStyleSheet(Theme.BUTTON_STYLE)
        self.send_button.clicked.connect(self.handle_send)
        
        # Botón de deshacer
        self.undo_button = QPushButton()
        self.undo_button.setStyleSheet(Theme.ICON_BUTTON_STYLE)
        undo_icon = QIcon()
        undo_icon.addFile("src/assets/undo.svg", QSize(16, 16))
        self.undo_button.setIcon(undo_icon)
        self.undo_button.setToolTip("Deshacer")
        
        # Botón de rehacer
        self.redo_button = QPushButton()
        self.redo_button.setStyleSheet(Theme.ICON_BUTTON_STYLE)
        redo_icon = QIcon()
        redo_icon.addFile("src/assets/redo.svg", QSize(16, 16))
        self.redo_button.setIcon(redo_icon)
        self.redo_button.setToolTip("Rehacer")
        
        buttons_layout.addWidget(self.undo_button)
        buttons_layout.addWidget(self.redo_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.send_button)
        
        input_layout.addWidget(self.input_field)
        input_layout.addLayout(buttons_layout)
        
        # Botones de acciones
        actions_layout = QHBoxLayout()
        
        self.analyze_btn = QPushButton("Predicciones")
        self.analyze_btn.setToolTip("Analiza y predice eventos futuros")
        self.analyze_btn.clicked.connect(self.handle_analyze)
        
        self.optimize_btn = QPushButton("Optimizar")
        self.optimize_btn.setToolTip("Optimiza la distribución de eventos")
        self.optimize_btn.clicked.connect(self.handle_optimize)
        
        self.suggest_btn = QPushButton("Sugerir")
        self.suggest_btn.setToolTip("Sugiere mejores horarios para eventos")
        self.suggest_btn.clicked.connect(self.handle_suggest)
        
        for btn in [self.analyze_btn, self.optimize_btn, self.suggest_btn]:
            btn.setStyleSheet(Theme.QUICK_ACTION_BUTTON_STYLE)
            actions_layout.addWidget(btn)
        
        layout.addWidget(self.chat_area, stretch=1)
        layout.addWidget(input_area)
        layout.addLayout(actions_layout)
            
        # Indicador de pensamiento
        self.thinking_indicator = QLabel("Pensando")
        self.thinking_indicator.setStyleSheet("""
            QLabel {
                color: #5f6368;
                padding: 8px;
                font-style: italic;
            }
        """)
        self.thinking_indicator.hide()
        
        layout.addWidget(self.thinking_indicator)

    def handle_input_key_press(self, event):
        """Maneja eventos de teclado en el input"""
        if event.key() == Qt.Key.Key_Return and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.handle_send()
        else:
            # Llamar al evento original para otros casos
            QTextEdit.keyPressEvent(self.input_field, event)

    def handle_send(self):
        """Maneja el envío de mensajes"""
        text = self.input_field.toPlainText().strip()
        if text:
            self.add_message(text, True)
            self.input_field.clear()
            self.start_thinking_animation()
            
            # Usar QTimer para procesar la respuesta de manera asíncrona
            QTimer.singleShot(0, lambda: self.process_ai_response(text))

    def process_ai_response(self, text):
        """Procesa la respuesta del AI"""
        try:
            response = self.ai_assistant.process_message(text)
            self.stop_thinking_animation()
            self.add_message(response, False)
        except Exception as e:
            self.stop_thinking_animation()
            self.add_message(f"Error: {str(e)}", False)

    def start_thinking_animation(self):
        """Inicia la animación de 'pensando'"""
        self.thinking_indicator.show()
        self.thinking_timer.start(500)

    def stop_thinking_animation(self):
        """Detiene la animación de 'pensando'"""
        self.thinking_timer.stop()
        self.thinking_indicator.hide()

    def update_thinking_indicator(self):
        """Actualiza los puntos del indicador de pensamiento"""
        self.thinking_dots = (self.thinking_dots + 1) % 4
        self.thinking_indicator.setText("Pensando" + "." * self.thinking_dots)

    def add_message(self, text: str, is_user: bool = False):
        """Agrega un mensaje al chat"""
        container = QWidget()
        layout = QHBoxLayout(container)
        
        if is_user:
            layout.addStretch()
        
        message = QLabel(text)
        message.setWordWrap(True)
        message.setStyleSheet(
            Theme.CHAT_MESSAGE_USER_STYLE if is_user 
            else Theme.CHAT_MESSAGE_AI_STYLE
        )
        
        # Limitar el ancho máximo del mensaje
        message.setMaximumWidth(int(self.width() * 0.7))
        
        layout.addWidget(message)
        
        if not is_user:
            layout.addStretch()
        
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, container)
        self.message_history.append((text, is_user))
        
        # Scroll al último mensaje
        QTimer.singleShot(100, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        """Desplaza el chat al último mensaje"""
        scrollbar = self.chat_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def handle_analyze(self):
        """Maneja el análisis de eventos"""
        try:
            if not self.calendar_analyzer.calendar_manager:
                self.add_message("Error: Por favor, autentícate primero con Google Calendar", False)
                return

            # Evitar múltiples análisis simultáneos
            if hasattr(self, 'analysis_worker') and self.analysis_worker and self.analysis_worker.isRunning():
                logger.warning("Análisis ya en proceso")
                return

            # Deshabilitar botones
            self.analyze_btn.setEnabled(False)
            self.send_button.setEnabled(False)
            self.analyze_btn.setStyleSheet(Theme.QUICK_ACTION_BUTTON_STYLE)

            # Agregar mensaje de carga
            self.dots_count = 0
            loading_message = "⌛ Espera.\n\nTiempo: 0s\n\nIniciando análisis..."
            self.add_message(loading_message, False)
            
            # Crear y configurar worker
            self.analysis_worker = AnalysisWorker(self.calendar_analyzer)
            self.analysis_worker.statusUpdated.connect(self._update_loading_message)
            self.analysis_worker.finished.connect(self._handle_analysis_finished)
            self.analysis_worker.error.connect(self._handle_analysis_error)
            
            # Iniciar timer para actualizar tiempo y animación
            self.start_time = datetime.now()
            self.loading_timer = QTimer()
            self.loading_timer.timeout.connect(self._update_loading_time)
            self.loading_timer.start(500)  # 500ms para una animación más fluida
            
            logger.info("Iniciando worker de análisis")
            self.analysis_worker.start()

        except Exception as e:
            self._cleanup_analysis(f"Error iniciando análisis: {str(e)}")

    def _update_loading_message(self, status: str):
        """Actualiza el mensaje de carga con el nuevo estado"""
        elapsed = (datetime.now() - self.start_time).seconds
        dots = "." * ((self.dots_count % 3) + 1)
        loading_message = f"⌛ Espera{dots}\n\nTiempo: {elapsed}s\n\n{status}"
        
        last_message = self.chat_area.findChildren(QLabel)[-1]
        last_message.setText(loading_message)

    def _update_loading_time(self):
        """Actualiza el tiempo y la animación de puntos"""
        if hasattr(self, 'start_time'):
            self.dots_count = (self.dots_count + 1) % 3
            elapsed = (datetime.now() - self.start_time).seconds
            last_message = self.chat_area.findChildren(QLabel)[-1]
            current_text = last_message.text()
            status = current_text.split("\n\n")[-1]
            dots = "." * ((self.dots_count % 3) + 1)
            new_text = f"⌛ Espera{dots}\n\nTiempo: {elapsed}s\n\n{status}"
            last_message.setText(new_text)

    def _handle_analysis_finished(self, result):
        """Maneja la finalización exitosa del análisis"""
        try:
            # Detener timer
            if hasattr(self, 'loading_timer'):
                self.loading_timer.stop()
            
            # Reemplazar mensaje de carga con el resultado
            last_message = self.chat_area.findChildren(QLabel)[-1]
            last_message.setText(result)
        finally:
            self._cleanup_analysis()

    def _handle_analysis_error(self, error_msg):
        """Maneja errores en el análisis"""
        self._cleanup_analysis(error_msg)

    def _cleanup_analysis(self, error_msg=None):
        """Limpia el estado después del análisis"""
        try:
            if error_msg:
                self.add_message(error_msg, False)
                logger.error(error_msg)

            # Restaurar botones
            self.analyze_btn.setEnabled(True)
            self.send_button.setEnabled(True)
            self.analyze_btn.setStyleSheet(Theme.QUICK_ACTION_BUTTON_STYLE)

            # Detener timer si existe
            if hasattr(self, 'loading_timer') and self.loading_timer:
                self.loading_timer.stop()
                self.loading_timer = None

            # Limpiar worker
            if self.analysis_worker:
                if self.analysis_worker.isRunning():
                    self.analysis_worker.stop()
                    self.analysis_worker.wait()
                self.analysis_worker.deleteLater()
                self.analysis_worker = None

        except Exception as e:
            logger.error(f"Error en cleanup: {str(e)}")

    def update_calendar_manager(self, calendar_manager):
        """Actualiza el calendar_manager después de la autenticación"""
        self.calendar_analyzer = CalendarAnalyzer(calendar_manager)

    def resizeEvent(self, event):
        """Asegurar que el overlay cubra todo el widget"""
        super().resizeEvent(event)
        # Solo redimensionar si el overlay existe y no ha sido eliminado
        if hasattr(self, 'loading_overlay') and self.loading_overlay:
            try:
                self.loading_overlay.resize(self.size())
            except RuntimeError:
                # Si el overlay fue eliminado, eliminamos la referencia
                self.loading_overlay = None

    def _create_overlays(self):
        """Crea o recrea los overlays si no existen"""
        if not self.loading_overlay:
            self.loading_overlay = LoadingOverlay(self)
            self.loading_overlay.hide()
        
        if not self.help_overlay:
            self.help_overlay = GenericOverlay(self)
            self.help_overlay.hide()

    def show_button_help(self, button: QPushButton):
        """Muestra el overlay de ayuda para el botón"""
        help_text = self.button_help.get(button.text())
        if help_text:
            # Asegurar que el overlay existe
            if not self.help_overlay:
                self._create_overlays()
            self.help_overlay.show_message(help_text, style="runic")

    def hide_button_help(self):
        """Oculta el overlay de ayuda"""
        if self.help_overlay:
            self.help_overlay.hide_message() 

    def handle_optimize(self):
        """Maneja la optimización de eventos"""
        self.add_message("Función de optimización en desarrollo...", False)

    def handle_suggest(self):
        """Maneja las sugerencias de horarios"""
        self.add_message("Función de sugerencias en desarrollo...", False) 