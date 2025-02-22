from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QMessageBox, QHBoxLayout, QLabel, QDialog, QPushButton, QMenuBar
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QThread
from config.constants import APP_NAME, DEFAULT_WINDOW_SIZE
from config.settings import Settings
from .styles.theme import Theme
from core.google_auth import GoogleAuthManager
from core.google_calendar import GoogleCalendarManager
from utils.logger import logger
from .components.calendar_widget import CalendarWidget
from .components.chat_sidebar import ChatSidebar
from datetime import datetime, timezone
from core.database import DatabaseManager
from .components.dev_panel import DevPanel
from .components.top_bar import TopBar
from .components.settings_panel import SettingsPanel
from .components.debug_panel import DebugPanel
from .workers.search_worker import SearchWorker
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.google_auth = GoogleAuthManager()
        self.calendar_manager = None
        self.calendar_widget = None
        self.chat_sidebar = None
        self.settings = Settings()
        self.settings.settingsChanged.connect(self.on_settings_changed)  # Conectar a la señal
        self.clean_logs()
        self.set_app_icon()
        self.init_ui()
        self.check_authentication()
        self.apply_theme()
        self.calendar_widget.monthChanged.connect(self.on_month_changed)
        self.update_api_status()
        self.calendar_widget.refreshRequested.connect(self.refresh_calendar)
        self.search_thread = None
        self.search_worker = None
        self.current_search = None  # Para rastrear la búsqueda actual

    def clean_logs(self):
        """Limpia los archivos de log al inicio"""
        try:
            # Limpiar raw_events.json
            with open('logs/raw_events.json', 'w') as f:
                f.write('[]')
            logger.info("Cleaned raw_events.json")
        except Exception as e:
            logger.error(f"Error cleaning logs: {str(e)}")

    def apply_theme(self):
        """Aplica el tema claro a toda la aplicación"""
        self.setStyleSheet(Theme.MAIN_WINDOW_STYLE)
        self.menuBar().setStyleSheet(Theme.MENUBAR_STYLE)

    def init_ui(self):
        # Set window properties
        self.setWindowTitle(APP_NAME)
        self.resize(*DEFAULT_WINDOW_SIZE)

        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # Eliminar márgenes

        # Initialize UI components
        self.setup_menubar()
        self.setup_toolbar()
        self.setup_statusbar()
        
        # Agregar TopBar primero
        self.top_bar = TopBar()
        self.main_layout.addWidget(self.top_bar)
        self.top_bar.logoutRequested.connect(self.handle_logout)
        self.top_bar.searchRequested.connect(self.handle_search)
        
        # Contenedor principal
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.addWidget(content_widget)
        
        # Área del calendario
        calendar_widget = QWidget()
        calendar_layout = QVBoxLayout(calendar_widget)
        self.calendar_widget = CalendarWidget(settings=self.settings)
        calendar_layout.addWidget(self.calendar_widget)
        
        # Barra lateral del chat
        self.chat_sidebar = ChatSidebar(
            db_manager=self.db_manager,
            calendar_manager=self.calendar_manager
        )
        self.chat_sidebar.messageSubmitted.connect(self.handle_chat_message)
        
        # Agregar widgets al layout horizontal
        content_layout.addWidget(calendar_widget, stretch=2)
        content_layout.addWidget(self.chat_sidebar, stretch=1)

        # Conectar señales del calendario
        self.calendar_widget.dateSelected.connect(self.on_date_selected)
        self.calendar_widget.eventClicked.connect(self.on_event_clicked)

        # Conectar el botón de refresh de la TopBar con el calendario
        refresh_button = self.top_bar.findChild(QPushButton, "refresh_button")
        if refresh_button:
            refresh_button.clicked.connect(self.refresh_calendar)

    def setup_menubar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu('&View')
        toggle_theme_action = QAction('Toggle Theme', self)
        toggle_theme_action.setShortcut('Ctrl+T')
        toggle_theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(toggle_theme_action)

        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        dev_panel_action = QAction('Developer Panel', self)
        dev_panel_action.triggered.connect(self.show_dev_panel)
        tools_menu.addAction(dev_panel_action)
        debug_action = QAction('Debug Panel', self)
        debug_action.triggered.connect(self.open_debug_panel)
        tools_menu.addAction(debug_action)

        # Add Google Calendar menu
        calendar_menu = menubar.addMenu('&Calendar')
        
        # Login action
        login_action = QAction('Login with Google', self)
        login_action.triggered.connect(self.handle_authentication)
        calendar_menu.addAction(login_action)
        
        # Logout action
        logout_action = QAction('Logout', self)
        logout_action.triggered.connect(self.handle_logout)
        calendar_menu.addAction(logout_action)
        
        # Refresh action
        refresh_action = QAction('Refresh Calendar', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_calendar)
        calendar_menu.addAction(refresh_action)

    def setup_toolbar(self):
        toolbar = self.addToolBar('Main Toolbar')
        toolbar.setMovable(False)
        # Add toolbar items later...

    def setup_statusbar(self):
        self.statusBar().showMessage('Ready')
        
        # Agregar separador y estado de API
        self.statusBar().addPermanentWidget(QLabel(" | "))
        self.api_status_label = QLabel()
        self.statusBar().addPermanentWidget(self.api_status_label)
        self.update_api_status()

    def update_api_status(self):
        """Actualiza el indicador de modo de API en la barra de estado"""
        if self.settings.use_mock_api:
            self.api_status_label.setText("API: Emulada")
            self.api_status_label.setStyleSheet("color: orange;")
        else:
            self.api_status_label.setText("API: Real")
            self.api_status_label.setStyleSheet("color: green;")

    def toggle_theme(self):
        # This method is now empty as the theme is applied automatically
        pass

    def check_authentication(self):
        """Verifica la autenticación y muestra diálogos apropiados"""
        try:
            # Preguntar si quiere iniciar sesión
            if not self.google_auth.is_authenticated():
                response = QMessageBox.question(
                    self,
                    'Iniciar Sesión',
                    '¿Deseas iniciar sesión con Google Calendar?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if response == QMessageBox.StandardButton.Yes:
                    self.handle_authentication()
                else:
                    QMessageBox.warning(
                        self,
                        'Acceso Limitado',
                        'La aplicación funcionará en modo limitado sin acceso al calendario.'
                    )
            else:
                self.setup_calendar_manager()
                
        except Exception as e:
            logger.error(f"Error en autenticación: {str(e)}")
            QMessageBox.critical(
                self,
                'Error de Autenticación',
                f'Error al verificar autenticación: {str(e)}'
            )

    def handle_authentication(self):
        """Maneja el proceso de autenticación"""
        try:
            credentials = self.google_auth.get_credentials()
            if credentials and credentials.valid:
                self.setup_calendar_manager()
                QMessageBox.information(
                    self,
                    'Autenticación Exitosa',
                    'Has iniciado sesión correctamente en Google Calendar'
                )
                self.load_calendar_data()
        except Exception as e:
            logger.error(f"Error en autenticación: {str(e)}")
            QMessageBox.critical(
                self,
                'Error de Autenticación',
                f'Error al autenticar: {str(e)}'
            )

    def setup_calendar_manager(self):
        """Configura el manager del calendario y actualiza UI"""
        self.calendar_manager = GoogleCalendarManager(self.google_auth)
        self.chat_sidebar.update_calendar_manager(self.calendar_manager)
        
        # Obtener info del usuario
        user_info = self.google_auth.get_user_info()
        self.top_bar.update_profile(user_info)
        
        self.load_calendar_data()

    def load_calendar_data(self):
        """Load calendar data after authentication"""
        if self.calendar_manager:
            try:
                events = self.calendar_manager.get_events()
                self.calendar_widget.set_events(events)
                logger.info(f"Loaded {len(events)} events")
            except Exception as e:
                logger.error(f"Error loading calendar data: {str(e)}")
                QMessageBox.warning(
                    self,
                    'Calendar Error',
                    f'Error loading calendar data: {str(e)}'
                )

    def on_date_selected(self, selected_date):
        """Maneja la selección de una fecha en el calendario"""
        logger.info(f"Fecha seleccionada: {selected_date}")
        # TODO: Mostrar eventos del día seleccionado

    def on_event_clicked(self, event):
        """Maneja el clic en un evento"""
        logger.info(f"Evento seleccionado: {event.title}")
        # TODO: Mostrar detalles del evento 

    def handle_chat_message(self, message: str):
        """Maneja los mensajes del chat"""
        # TODO: Integrar con el asistente AI
        response = "Respuesta del asistente..."
        self.chat_sidebar.add_message(response)

    def on_month_changed(self, new_month: datetime):
        """Maneja el cambio de mes en el calendario"""
        if self.calendar_manager:
            try:
                # Calcular el rango del mes
                month_start = new_month
                if month_start.month == 12:
                    month_end = datetime(
                        month_start.year + 1, 1, 1,
                        tzinfo=timezone.utc
                    )
                else:
                    month_end = datetime(
                        month_start.year,
                        month_start.month + 1, 1,
                        tzinfo=timezone.utc
                    )
                
                # Cargar eventos del mes
                events = self.calendar_manager.get_events(
                    start_date=month_start,
                    end_date=month_end
                )
                self.calendar_widget.set_events(events)
                logger.info(f"Loaded {len(events)} events for {new_month.strftime('%B %Y')}")
            except Exception as e:
                logger.error(f"Error loading calendar data: {str(e)}")
                QMessageBox.warning(
                    self,
                    'Calendar Error',
                    f'Error loading calendar data: {str(e)}'
                ) 

    def show_dev_panel(self):
        """Muestra el panel de desarrollo"""
        dev_panel = DevPanel(self)
        dev_panel.setModal(True)
        if dev_panel.exec() == QDialog.DialogCode.Accepted:
            # Actualizar el estado de la API cuando se cierra el panel
            self.update_api_status() 

    def refresh_calendar(self):
        """Actualiza los eventos del calendario"""
        try:
            if not self.calendar_manager:
                self.check_authentication()
                return

            current_month = self.calendar_widget.current_date
            month_start = datetime(
                current_month.year(),
                current_month.month(),
                1,
                tzinfo=timezone.utc
            )
            
            if month_start.month == 12:
                month_end = datetime(
                    month_start.year + 1, 1, 1,
                    tzinfo=timezone.utc
                )
            else:
                month_end = datetime(
                    month_start.year,
                    month_start.month + 1, 1,
                    tzinfo=timezone.utc
                )

            events = self.calendar_manager.get_events(
                start_date=month_start,
                end_date=month_end
            )
            self.calendar_widget.set_events(events)
            logger.info(f"Calendario actualizado: {len(events)} eventos")
        except Exception as e:
            logger.error(f"Error actualizando calendario: {str(e)}")
            self.check_authentication()  # Intentar re-autenticar si hay error 

    def on_settings_changed(self):
        """Manejar cambios en la configuración"""
        self.update_api_status()  # Actualizar indicador de API
        # Actualizar otros componentes que dependan de la configuración 

    def set_app_icon(self):
        """Establece el ícono de la aplicación"""
        icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'app_icon.svg')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path)) 

    def handle_logout(self):
        """Maneja el cierre de sesión"""
        try:
            # Limpiar credenciales
            self.google_auth.clear_credentials()
            self.calendar_manager = None
            
            # Mostrar mensaje
            QMessageBox.information(
                self,
                'Sesión Cerrada',
                'Has cerrado sesión exitosamente. La aplicación se cerrará.'
            )
            
            # Cerrar la aplicación
            self.close()
            
        except Exception as e:
            logger.error(f"Error en logout: {str(e)}")
            QMessageBox.critical(
                self,
                'Error',
                f'Error al cerrar sesión: {str(e)}'
            )

    def handle_search(self, query: str):
        """Maneja la búsqueda de eventos"""
        try:
            if not self.calendar_manager:
                return

            # Si es la misma búsqueda, ignorar
            if self.current_search == query:
                return
            self.current_search = query

            # Detener thread anterior si existe
            if self.search_thread and self.search_thread.isRunning():
                self.search_thread.quit()
                self.search_worker.deleteLater()
                self.search_thread.deleteLater()
                self.search_thread.wait()

            # Crear thread y worker
            self.search_thread = QThread()
            self.search_worker = SearchWorker(self.calendar_manager, query)
            self.search_worker.moveToThread(self.search_thread)

            # Conectar señales
            self.search_thread.started.connect(self.search_worker.search)
            self.search_worker.finished.connect(self.show_search_results)
            self.search_worker.error.connect(self.handle_search_error)
            self.search_worker.finished.connect(lambda: self._cleanup_search())
            
            # Iniciar búsqueda
            self.search_thread.start()
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {str(e)}")
            self.statusBar().showMessage(f"Error en búsqueda: {str(e)}")

    def _cleanup_search(self):
        """Limpia los recursos de búsqueda"""
        if self.search_thread:
            self.search_thread.quit()
            self.search_worker.deleteLater()
            self.search_thread.deleteLater()
            self.search_thread.wait()
            self.search_thread = None
            self.search_worker = None
            self.current_search = None

    def show_search_results(self, search_results):
        """Muestra los resultados de búsqueda"""
        if not hasattr(self, 'search_results_widget'):
            from .components.search_results import SearchResultsWidget
            self.search_results_widget = SearchResultsWidget()
            self.search_results_widget.eventClicked.connect(self.calendar_widget.highlight_events)
        
        self.search_results_widget.update_results(search_results)
        self.search_results_widget.show_under_widget(self.top_bar.search_box)

    def handle_search_error(self, error_msg):
        """Maneja errores de búsqueda"""
        logger.error(f"Error en búsqueda: {error_msg}")
        self.statusBar().showMessage(f"Error en búsqueda: {error_msg}") 

    def closeEvent(self, event):
        """Se llama cuando se cierra la ventana"""
        self._cleanup_search()
        event.accept() 

    def open_debug_panel(self):
        debug_panel = DebugPanel(self)
        debug_panel.setWindowModality(Qt.WindowModality.NonModal)  # Asegurarse de que sea no modal
        debug_panel.show()  # Usar show() en lugar de exec() 