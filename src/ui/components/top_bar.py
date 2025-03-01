from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QMenu,
    QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QPainterPath, QColor
import requests
from io import BytesIO
import os
import logging
from ..styles.theme import Theme

logger = logging.getLogger(__name__)

class TopBar(QWidget):
    searchRequested = pyqtSignal(str)
    logoutRequested = pyqtSignal()
    refreshRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setFixedHeight(60)  # Aumentado de 50 a 60 para más espacio
        self.apply_styles()

    def apply_styles(self):
        # Aplicar estilos basados en el tema actual
        is_dark = Theme.is_dark_mode
        bg_color = Theme.DARK_BG if is_dark else Theme.LIGHT_BG
        border_color = Theme.DARK_BORDER if is_dark else Theme.LIGHT_BORDER
        text_color = Theme.DARK_TEXT if is_dark else Theme.LIGHT_TEXT
        secondary_text = Theme.DARK_SECONDARY_TEXT if is_dark else Theme.LIGHT_SECONDARY_TEXT
        hover_color = Theme.DARK_HOVER if is_dark else Theme.LIGHT_HOVER
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-bottom: 1px solid {border_color};
            }}
            QLineEdit {{
                padding: 8px 36px;
                border: 1px solid {border_color};
                border-radius: 20px;
                background: {hover_color};
                color: {text_color};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {Theme.DARK_ACCENT if is_dark else Theme.LIGHT_ACCENT};
                background-color: {Theme.DARK_BG if is_dark else Theme.LIGHT_BG};
            }}
            QPushButton {{
                border: none;
                padding: 8px;
                border-radius: 4px;
                background: transparent;
                color: {text_color};
            }}
            QPushButton:hover {{
                background: {hover_color};
            }}
            #logo_label {{
                font-size: 18px;
                font-weight: bold;
                color: {text_color};
            }}
            #action_button {{
                background-color: {Theme.DARK_ACCENT if is_dark else Theme.LIGHT_ACCENT};
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 500;
            }}
            #action_button:hover {{
                background-color: {Theme.DARK_ACCENT_HOVER if is_dark else Theme.LIGHT_ACCENT_HOVER};
            }}
            #logout_button {{
                color: {text_color};
                border-radius: 4px;
                padding: 8px;
            }}
            #logout_button:hover {{
                background-color: {hover_color};
            }}
        """)

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(16)  # Espacio entre secciones

        # 1. Logo y nombre (izquierda)
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(8)
        
        # Logo
        logo_icon = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'app_icon.svg')
        logo_icon.setPixmap(QIcon(icon_path).pixmap(24, 24))
        
        # Nombre de la app
        logo_text = QLabel("CalendarAI")
        logo_text.setObjectName("logo_label")
        
        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(logo_text)
        layout.addWidget(logo_container)

        # 2. Barra de búsqueda y botones (centro)
        center_container = QWidget()
        center_layout = QHBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(16)
        
        # Contenedor para la barra de búsqueda con icono
        search_container = QFrame()
        search_container.setFixedWidth(400)  # Aumentado de 300 a 400
        search_container_layout = QHBoxLayout(search_container)
        search_container_layout.setContentsMargins(0, 0, 0, 0)
        search_container_layout.setSpacing(0)
        
        # Barra de búsqueda mejorada
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Buscar eventos...")
        self.search_box.returnPressed.connect(self._handle_search)
        
        # Icono de búsqueda (ahora como label para posicionarlo mejor)
        search_icon = QLabel()
        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'search_icon.svg')
        search_icon.setPixmap(QIcon(icon_path).pixmap(16, 16))
        search_icon.setStyleSheet("""
            QLabel {
                margin-left: 12px;
                background: transparent;
                position: absolute;
            }
        """)
        
        # Agregar widgets al contenedor de búsqueda
        search_container_layout.addWidget(search_icon)
        search_container_layout.addWidget(self.search_box)
        
        # Botones de navegación
        nav_container = QWidget()
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(8)
        
        # Botones con iconos
        for icon, tooltip in [
            ("refresh", "Actualizar"),
            ("settings", "Configuración"),
            ("help", "Ayuda")
        ]:
            btn = QPushButton()
            btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', f'{icon}_icon.svg')))
            btn.setFixedSize(36, 36)
            btn.setToolTip(tooltip)
            
            if icon == "refresh":
                btn.setObjectName("refresh_button")
                btn.clicked.connect(self.refresh_clicked)
            elif icon == "settings":
                btn.clicked.connect(self.open_settings_panel)
            elif icon == "help":
                btn.clicked.connect(self.open_help)
                
            nav_layout.addWidget(btn)
        
        center_layout.addWidget(search_container)
        center_layout.addStretch()
        center_layout.addWidget(nav_container)
        
        layout.addWidget(center_container, 1)  # El centro ocupa el espacio disponible

        # 3. Perfil y botones de acción (derecha)
        right_container = QWidget()
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(16)
        
        # Botón de acción principal
        action_button = QPushButton("Nuevo Evento")
        action_button.setObjectName("action_button")
        action_button.setFixedHeight(36)
        
        # Perfil
        profile_container = QWidget()
        profile_layout = QHBoxLayout(profile_container)
        profile_layout.setContentsMargins(0, 0, 0, 0)
        profile_layout.setSpacing(8)
        
        self.profile_pic = QLabel()
        self.profile_pic.setFixedSize(36, 36)
        self.profile_pic.setStyleSheet("""
            QLabel {
                border-radius: 18px;
                background: #f0f0f0;
                border: 2px solid #e0e0e0;
                qproperty-scaledContents: true;
            }
        """)
        
        self.profile_name = QLabel("No conectado")
        self.profile_name.setStyleSheet("""
            font-weight: 500;
            border: none;
        """)
        
        # Botón de cerrar sesión
        self.logout_button = QPushButton()
        self.logout_button.setObjectName("logout_button")
        self.logout_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'logout_icon.svg')))
        self.logout_button.setFixedSize(36, 36)
        self.logout_button.setToolTip("Cerrar Sesión")
        self.logout_button.clicked.connect(lambda: self.logoutRequested.emit())
        
        profile_layout.addWidget(self.profile_pic)
        profile_layout.addWidget(self.profile_name)
        
        right_layout.addWidget(action_button)
        right_layout.addWidget(profile_container)
        right_layout.addWidget(self.logout_button)  # Añadir botón de cerrar sesión
        
        layout.addWidget(right_container)

    def update_profile(self, user_info):
        """Actualiza la información del perfil"""
        try:
            if user_info.get('picture'):
                response = requests.get(user_info['picture'])
                img = QPixmap()
                img.loadFromData(BytesIO(response.content).read())
                
                # Crear una imagen circular
                rounded_img = QPixmap(36, 36)
                rounded_img.fill(Qt.GlobalColor.transparent)
                painter = QPainter(rounded_img)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                path = QPainterPath()
                path.addEllipse(2, 2, 32, 32)  # Ajustado para el borde
                painter.setClipPath(path)
                painter.drawPixmap(2, 2, 32, 32, img.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                painter.end()
                self.profile_pic.setPixmap(rounded_img)
            else:
                default_avatar = QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'default_avatar.svg'))
                self.profile_pic.setPixmap(default_avatar.pixmap(36, 36))
            
            self.profile_name.setText(user_info.get('name', "No conectado"))
        except Exception as e:
            logger.error(f"Error actualizando perfil: {e}")
            default_avatar = QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'default_avatar.svg'))
            self.profile_pic.setPixmap(default_avatar.pixmap(36, 36))
            self.profile_name.setText("Error al cargar perfil")

    def _handle_search(self):
        """Maneja la búsqueda de eventos"""
        query = self.search_box.text().strip()
        if query:
            self.searchRequested.emit(query)
            # El widget de resultados se mostrará bajo la barra de búsqueda
            if hasattr(self.parent(), 'search_results_widget'):
                self.parent().search_results_widget.show_under_widget(self.search_box)

    def open_settings_panel(self):
        from .settings_panel import SettingsPanel
        settings_panel = SettingsPanel(self)
        settings_panel.exec()
        
    def refresh_clicked(self):
        """Emite la señal de refresh cuando se hace clic en el botón de actualizar"""
        self.refreshRequested.emit()
        
    def open_help(self):
        """Abre el panel de ayuda"""
        from .help_overlay import RunicHelpOverlay
        try:
            help_overlay = RunicHelpOverlay(self.window())
            help_overlay.show()
        except Exception as e:
            logger.error(f"Error al abrir ayuda: {str(e)}")
            
    def update_theme(self):
        """Actualiza los estilos cuando cambia el tema"""
        self.apply_styles()
