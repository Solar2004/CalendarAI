from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QMessageBox, QHBoxLayout, QLabel, QDialog
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
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
        self.init_ui()
        self.check_authentication()
        self.apply_theme()
        self.calendar_widget.monthChanged.connect(self.on_month_changed)
        self.update_api_status()
        self.calendar_widget.refreshRequested.connect(self.refresh_calendar)

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

        # Initialize UI components
        self.setup_menubar()
        self.setup_toolbar()
        self.setup_statusbar()
        
        # Crear layout horizontal principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        horizontal_layout = QHBoxLayout(main_widget)
        
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
        horizontal_layout.addWidget(calendar_widget, stretch=2)
        horizontal_layout.addWidget(self.chat_sidebar, stretch=1)

        # Conectar señales del calendario
        self.calendar_widget.dateSelected.connect(self.on_date_selected)
        self.calendar_widget.eventClicked.connect(self.on_event_clicked)

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
        
        # Add Developer Panel action
        dev_panel_action = QAction('Developer Panel', self)
        dev_panel_action.triggered.connect(self.show_dev_panel)
        tools_menu.addAction(dev_panel_action)

        # Add Google Calendar menu
        calendar_menu = menubar.addMenu('&Calendar')
        login_action = QAction('Login with Google', self)
        login_action.triggered.connect(self.handle_authentication)
        calendar_menu.addAction(login_action)
        
        # Agregar acción de refresh
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
        """Verifica la autenticación y la renueva si es necesario"""
        try:
            if not self.google_auth.is_authenticated():
                self.handle_authentication()
            else:
                self.setup_calendar_manager()
        except Exception as e:
            logger.error(f"Error en autenticación: {str(e)}")
            self.handle_authentication()

    def handle_authentication(self):
        """Maneja el proceso de autenticación"""
        try:
            credentials = self.google_auth.get_credentials()
            if credentials and credentials.valid:
                self.setup_calendar_manager()
            else:
                QMessageBox.warning(
                    self,
                    'Autenticación Requerida',
                    'Por favor, inicia sesión con Google Calendar'
                )
        except Exception as e:
            logger.error(f"Error en autenticación: {str(e)}")
            QMessageBox.critical(
                self,
                'Error de Autenticación',
                f'Error al autenticar: {str(e)}'
            )

    def setup_calendar_manager(self):
        """Configura el manager del calendario"""
        self.calendar_manager = GoogleCalendarManager(self.google_auth)
        self.chat_sidebar.update_calendar_manager(self.calendar_manager)
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