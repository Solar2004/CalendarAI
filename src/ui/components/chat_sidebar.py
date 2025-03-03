from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QScrollArea, QLabel, QGraphicsDropShadowEffect, QLineEdit,
    QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint, QTimer, QPointF, QThread
from PyQt6.QtGui import QIcon, QColor
from ..styles.theme import Theme
from core.ai_assistant import AIAssistant
from core.calendar_analyzer import CalendarAnalyzer
from .loading_overlay import LoadingOverlay
from .analysis_worker import AnalysisWorker
from .chat_worker import Worker
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class ChatMessage(QWidget):
    def __init__(self, text: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.text = text
        self.is_user = is_user
        self.timestamp = datetime.now()
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        
        # Message container
        message_container = QWidget()
        message_layout = QVBoxLayout(message_container)
        message_layout.setContentsMargins(0, 0, 0, 0)
        message_layout.setSpacing(2)
        
        # Message content
        self.message_label = QLabel(text)
        self.message_label.setWordWrap(True)
        self.message_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | 
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        self.message_label.setStyleSheet(
            Theme.CHAT_MESSAGE_USER_STYLE if is_user 
            else Theme.CHAT_MESSAGE_AI_STYLE
        )
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(4)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 2)
        self.message_label.setGraphicsEffect(shadow)
        
        message_layout.addWidget(self.message_label)
        
        # Timestamp and actions container
        footer_container = QWidget()
        footer_layout = QHBoxLayout(footer_container)
        footer_layout.setContentsMargins(4, 0, 4, 0)
        footer_layout.setSpacing(8)
        
        # Timestamp
        self.timestamp_label = QLabel(self._format_timestamp())
        self.timestamp_label.setStyleSheet(Theme.CHAT_TIMESTAMP_STYLE)
        
        # Copy button
        self.copy_button = QPushButton("Copy")
        self.copy_button.setFixedSize(40, 20)
        self.copy_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #70757a;
                font-size: 10px;
                padding: 0;
            }
            QPushButton:hover {
                color: #1a73e8;
                text-decoration: underline;
            }
        """)
        self.copy_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_button.clicked.connect(self._copy_text)
        
        # Add widgets to footer
        footer_layout.addWidget(self.timestamp_label)
        footer_layout.addStretch()
        footer_layout.addWidget(self.copy_button)
        
        # Add containers to main layout
        message_layout.addWidget(footer_container)
        main_layout.addWidget(message_container)
        
        # Update timestamp every minute
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timestamp)
        self.timer.start(60000)  # Update every minute
    
    def _format_timestamp(self):
        """Format the timestamp as a relative time (e.g., 'just now', '1 min ago')"""
        now = datetime.now()
        diff = now - self.timestamp
        
        if diff.total_seconds() < 60:
            return "just now"
        elif diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} min ago"
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            days = int(diff.total_seconds() / 86400)
            return f"{days} day{'s' if days > 1 else ''} ago"
    
    def _update_timestamp(self):
        """Update the timestamp label"""
        self.timestamp_label.setText(self._format_timestamp())
    
    def _copy_text(self):
        """Copy the message text to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text)

class ChatSidebar(QWidget):
    messageSubmitted = pyqtSignal(str)
    themeToggled = pyqtSignal(bool)  # Signal to notify theme changes (True = dark mode)

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
        
        # Initialize thinking animation variables
        self.thinking_dots = 0
        self.thinking_timer = QTimer()
        self.thinking_timer.timeout.connect(self.update_thinking_indicator)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with theme toggle
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Title
        title_label = QLabel("Chat")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        # Theme toggle button
        self.theme_toggle_btn = QPushButton()
        self.theme_toggle_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'light_mode_icon.svg')))
        self.theme_toggle_btn.setFixedSize(32, 32)
        self.theme_toggle_btn.setStyleSheet("border: none;")
        self.theme_toggle_btn.setToolTip("Cambiar tema")
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.theme_toggle_btn)
        
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
        
        # Contenedor para el campo de texto y botones
        message_container = QHBoxLayout()
        
        # Botón de clip
        clip_button = QPushButton()
        clip_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'clip_icon.svg')))
        clip_button.setFixedSize(32, 32)
        clip_button.setStyleSheet("border: none;")  # Sin borde
        clip_button.clicked.connect(self.handle_clip)  # Conectar a la función de clip

        # Campo de texto
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Escribe un mensaje...")
        self.message_input.setStyleSheet("border-radius: 15px; padding: 5px;")
        self.message_input.returnPressed.connect(self.handle_send)

        # Botón de enviar
        self.send_button = QPushButton()
        self.send_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'send_icon.svg')))
        self.send_button.setFixedSize(32, 32)
        self.send_button.setStyleSheet("border: none;")  # Sin borde
        self.send_button.clicked.connect(self.handle_send)  # Conectar a la función de enviar

        # Agregar widgets al contenedor
        message_container.addWidget(clip_button)
        message_container.addWidget(self.message_input)
        message_container.addWidget(self.send_button)

        input_layout.addLayout(message_container)
        
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
        
        layout.addWidget(header_container)
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

    def handle_clip(self):
        """Maneja la acción del botón de clip"""
        # Lógica para adjuntar archivos
        pass

    def handle_send(self):
        """Maneja la acción del botón de enviar"""
        message = self.message_input.text()
        if message:
            logger.info("Mensaje enviado por el usuario: %s", message)
            self.message_input.clear()  # Limpiar el campo de texto
            self.add_message(message, True)
            self.start_thinking_animation()

            # Crear un hilo para procesar la respuesta
            self.thread = QThread()
            self.worker = Worker(self.ai_assistant, message)
            self.worker.moveToThread(self.thread)

            # Conectar señales
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.process_ai_response)
            self.worker.error.connect(self.handle_error)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.finished.connect(self.thread.quit)

            # Iniciar el hilo
            self.thread.start()

    def process_ai_response(self, response):
        """Procesa la respuesta del AI"""
        try:
            logger.info("Procesando respuesta de la IA para el mensaje: %s", response)
            self.stop_thinking_animation()
            self.add_message(response, False)
        except Exception as e:
            logger.error("Error al procesar la respuesta de la IA: %s", str(e))
            self.stop_thinking_animation()
            self.add_message(f"Error: {str(e)}", False)

    def handle_error(self, error_msg):
        """Maneja errores en el procesamiento de la IA"""
        self.stop_thinking_animation()
        self.add_message(f"Error: {error_msg}", False)

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
        # Create message container
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add alignment
        if is_user:
            container_layout.addStretch()
        
        # Create message widget
        message_widget = ChatMessage(text, is_user)
        container_layout.addWidget(message_widget)
        
        if not is_user:
            container_layout.addStretch()
        
        # Add to chat layout
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, container)
        
        # Store in history
        self.message_history.append((text, is_user))
        
        # Scroll to bottom
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
        
        # Find the last message widget
        last_container = self.chat_layout.itemAt(self.chat_layout.count() - 2).widget()
        for child in last_container.findChildren(ChatMessage):
            if hasattr(child, 'message_label'):
                child.message_label.setText(loading_message)
                break

    def _update_loading_time(self):
        """Actualiza el tiempo y la animación de puntos"""
        if hasattr(self, 'start_time'):
            self.dots_count = (self.dots_count + 1) % 3
            elapsed = (datetime.now() - self.start_time).seconds
            
            # Find the last message widget
            last_container = self.chat_layout.itemAt(self.chat_layout.count() - 2).widget()
            for child in last_container.findChildren(ChatMessage):
                if hasattr(child, 'message_label'):
                    current_text = child.message_label.text()
                    status = current_text.split("\n\n")[-1]
                    dots = "." * ((self.dots_count % 3) + 1)
                    new_text = f"⌛ Espera{dots}\n\nTiempo: {elapsed}s\n\n{status}"
                    child.message_label.setText(new_text)
                    break

    def _handle_analysis_finished(self, result):
        """Maneja la finalización exitosa del análisis"""
        try:
            # Detener timer
            if hasattr(self, 'loading_timer'):
                self.loading_timer.stop()
            
            # Reemplazar mensaje de carga con el resultado
            last_container = self.chat_layout.itemAt(self.chat_layout.count() - 2).widget()
            for child in last_container.findChildren(ChatMessage):
                if hasattr(child, 'message_label'):
                    child.message_label.setText(result)
                    child.text = result  # Update the stored text for copy functionality
                    break
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
        if not hasattr(self, 'loading_overlay') or not self.loading_overlay:
            self.loading_overlay = LoadingOverlay(self)
            self.loading_overlay.hide()
        
        if not hasattr(self, 'help_overlay') or not self.help_overlay:
            from .help_overlay import HelpOverlay
            self.help_overlay = HelpOverlay(self)
            self.help_overlay.hide()

    def show_button_help(self, button: QPushButton):
        """Muestra el overlay de ayuda para el botón"""
        if not hasattr(self, 'button_help'):
            self.button_help = {
                "Predicciones": "Analiza tus eventos y predice patrones futuros",
                "Optimizar": "Sugiere mejoras en la distribución de tus eventos",
                "Sugerir": "Recomienda mejores horarios para tus actividades"
            }
            
        help_text = self.button_help.get(button.text())
        if help_text:
            # Asegurar que el overlay existe
            self._create_overlays()
            self.help_overlay.show_message(help_text)

    def hide_button_help(self):
        """Oculta el overlay de ayuda"""
        if hasattr(self, 'help_overlay') and self.help_overlay:
            self.help_overlay.hide()

    def handle_optimize(self):
        """Maneja la optimización de eventos"""
        try:
            if not self.calendar_analyzer.calendar_manager:
                self.add_message("Error: Por favor, autentícate primero con Google Calendar", False)
                return
                
            # Agregar mensaje del usuario
            self.add_message("Optimiza mi calendario y sugiere mejoras", True)
            
            # Mostrar mensaje de carga
            self.add_message("Analizando eventos y buscando oportunidades de optimización...", False)
            
            # Obtener eventos actuales
            events = self.calendar_analyzer.calendar_manager.get_events()
            
            if not events:
                self.add_message("No hay eventos para analizar. Agrega algunos eventos a tu calendario primero.", False)
                return
                
            # Preparar prompt para el asistente
            prompt = f"""
            Analiza estos eventos de calendario y sugiere optimizaciones:
            
            {self._format_events_for_analysis(events)}
            
            Proporciona sugerencias específicas para:
            1. Mejorar la distribución de eventos
            2. Evitar sobrecargas de trabajo
            3. Optimizar tiempos de descanso
            4. Agrupar tareas similares
            5. Identificar conflictos potenciales
            
            Responde en español con un formato claro y conciso.
            """
            
            # Procesar con el asistente
            response = self.ai_assistant.process_message(prompt)
            
            # Mostrar respuesta
            self.add_message(response, False)
            
        except Exception as e:
            logger.error(f"Error en optimización: {str(e)}")
            self.add_message(f"Error al optimizar eventos: {str(e)}", False)

    def handle_suggest(self):
        """Maneja las sugerencias de horarios basadas en análisis de tareas existentes"""
        try:
            if not self.calendar_analyzer.calendar_manager:
                self.add_message("Error: Por favor, autentícate primero con Google Calendar", False)
                return
                
            # Agregar mensaje del usuario
            self.add_message("Sugiere mejoras basadas en mis tareas actuales", True)
            
            # Mostrar mensaje de carga
            self.add_message("Analizando patrones de tareas y buscando oportunidades de mejora...", False)
            
            # Obtener eventos actuales
            events = self.calendar_analyzer.calendar_manager.get_events()
            
            if not events:
                self.add_message("No hay eventos para analizar. Agrega algunos eventos a tu calendario primero.", False)
                return
                
            # Preparar prompt para el asistente
            prompt = f"""
            Analiza estos eventos de calendario y sugiere mejoras basadas en patrones identificados:
            
            {self._format_events_for_analysis(events)}
            
            Proporciona sugerencias específicas para:
            1. Mejorar la productividad basada en patrones observados
            2. Identificar hábitos que podrían optimizarse
            3. Sugerir nuevos horarios para tipos de tareas recurrentes
            4. Recomendar cambios en la duración de ciertos tipos de eventos
            5. Identificar oportunidades para combinar o separar actividades
            
            Responde en español con un formato claro y conciso.
            """
            
            # Procesar con el asistente
            response = self.ai_assistant.process_message(prompt)
            
            # Mostrar respuesta
            self.add_message(response, False)
            
        except Exception as e:
            logger.error(f"Error en sugerencias: {str(e)}")
            self.add_message(f"Error al generar sugerencias: {str(e)}", False)
            
    def _format_events_for_analysis(self, events):
        """Formatea los eventos para el análisis"""
        formatted_events = []
        for event in events:
            formatted_events.append(f"- {event.title}: {event.start_datetime.strftime('%Y-%m-%d %H:%M')} a {event.end_datetime.strftime('%H:%M')}")
        
        return "\n".join(formatted_events)

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        is_dark_mode = Theme.toggle_theme()
        
        # Update icon based on current theme
        icon_name = "dark_mode_icon.svg" if is_dark_mode else "light_mode_icon.svg"
        self.theme_toggle_btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', icon_name)))
        
        # Update styles
        self.setStyleSheet(Theme.SIDEBAR_STYLE)
        
        # Update all message styles
        self.update_message_styles()
        
        # Emit signal for parent components to update
        self.themeToggled.emit(is_dark_mode)
    
    def update_message_styles(self):
        """Update styles for all message widgets"""
        # Find all ChatMessage widgets and update their styles
        for i in range(self.chat_layout.count() - 1):  # -1 to skip the stretch at the end
            container = self.chat_layout.itemAt(i).widget()
            if container:
                for message_widget in container.findChildren(ChatMessage):
                    if message_widget.is_user:
                        message_widget.message_label.setStyleSheet(Theme.CHAT_MESSAGE_USER_STYLE)
                    else:
                        message_widget.message_label.setStyleSheet(Theme.CHAT_MESSAGE_AI_STYLE)
                    
                    # Update timestamp style
                    if hasattr(message_widget, 'timestamp_label'):
                        message_widget.timestamp_label.setStyleSheet(Theme.CHAT_TIMESTAMP_STYLE)
