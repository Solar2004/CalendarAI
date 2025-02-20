from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QPainterPath
import requests
from io import BytesIO
import os
import logging

logger = logging.getLogger(__name__)

class TopBar(QWidget):
    searchRequested = pyqtSignal(str)
    logoutRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setFixedHeight(50)

        # Mejoras en CSS para evitar bordes grises
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-bottom: 1px solid transparent; /* Quita la línea gris */
            }
            QLineEdit {
                padding: 5px 30px 5px 10px;
                border: none;
                border-radius: 15px;
                background: #f5f5f5;
            }
            QPushButton {
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                background: transparent;
            }
            QPushButton:hover {
                background: #f0f0f0;
            }
        """)

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(20)  # Espacio entre secciones

        # 1. Perfil y nombre (izquierda)
        profile_container = QWidget()
        profile_container.setFixedWidth(200)
        profile_layout = QHBoxLayout(profile_container)
        profile_layout.setContentsMargins(0, 0, 0, 0)  # Evita espacios extra
        profile_layout.setSpacing(10)
        
        self.profile_pic = QLabel()
        self.profile_pic.setFixedSize(32, 32)
        self.profile_pic.setStyleSheet("""
            QLabel {
                border-radius: 16px;
                background: #f0f0f0;
                border: 2px solid #e0e0e0;  /* Agregamos borde */
                qproperty-scaledContents: true;  /* Para asegurar que la imagen se ajuste */
            }
        """)
        
        self.profile_name = QLabel("No conectado")
        self.profile_name.setStyleSheet("""
            color: #666;
            font-weight: bold;
            border: none;
        """)
        
        profile_layout.addWidget(self.profile_pic)
        profile_layout.addWidget(self.profile_name)
        layout.addWidget(profile_container)

        # 2. Barra de búsqueda y botones (centro)
        center_container = QWidget()
        center_container.setFixedWidth(500)  
        center_layout = QHBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)  # Quita márgenes
        center_layout.setSpacing(10)
        
        self.search_box = QLineEdit()
        self.search_box.setFixedWidth(300)
        self.search_box.setPlaceholderText("Buscar eventos...")
        self.search_box.returnPressed.connect(self._handle_search)
        self.search_box.setStyleSheet("""
            QLineEdit {
                border: none;
                border-radius: 15px;
                background: #f5f5f5;
            }
        """)

        search_icon = QPushButton()
        search_icon.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'search_icon.svg')))
        search_icon.setFixedSize(32, 32)
        search_icon.clicked.connect(self._handle_search)
        
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.addWidget(self.search_box)
        search_layout.addWidget(search_icon)

        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(5)
        
        for icon in ["refresh", "settings", "help"]:
            btn = QPushButton()
            btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', f'{icon}_icon.svg')))
            btn.setFixedSize(32, 32)
            if icon == "refresh":
                btn.setObjectName("refresh_button")  # Asignar nombre para poder encontrarlo
            buttons_layout.addWidget(btn)
        
        center_layout.addStretch()  
        center_layout.addWidget(search_container)
        center_layout.addWidget(buttons_container)
        center_layout.addStretch()
        
        layout.addWidget(center_container)

        # 3. Botones de ejemplo (derecha)
        right_container = QWidget()
        right_container.setFixedWidth(300)
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)  # Quita espacios extra
        right_layout.setSpacing(10)

        for i in range(3):
            btn = QPushButton(f"Example {i+1}")
            btn.setFixedHeight(32)
            btn.setStyleSheet("""
                QPushButton {
                    background: #f5f5f5;
                    border: none;
                    border-radius: 4px;
                    padding: 0 15px;
                }
                QPushButton:hover {
                    background: #e0e0e0;
                }
            """)
            right_layout.addWidget(btn)
        
        layout.addWidget(right_container)

    def update_profile(self, user_info):
        """Actualiza la información del perfil"""
        try:
            if user_info.get('picture'):
                response = requests.get(user_info['picture'])
                img = QPixmap()
                img.loadFromData(BytesIO(response.content).read())
                
                # Crear una imagen circular
                rounded_img = QPixmap(32, 32)
                rounded_img.fill(Qt.GlobalColor.transparent)
                painter = QPainter(rounded_img)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                path = QPainterPath()
                path.addEllipse(2, 2, 28, 28)  # Ajustado para el borde
                painter.setClipPath(path)
                painter.drawPixmap(2, 2, 28, 28, img.scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                painter.end()
                self.profile_pic.setPixmap(rounded_img)
            else:
                default_avatar = QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'default_avatar.svg'))
                self.profile_pic.setPixmap(default_avatar.pixmap(32, 32))
            
            self.profile_name.setText(user_info.get('name', "No conectado"))
            self.profile_pic.mousePressEvent = self._show_profile_menu
        except Exception as e:
            logger.error(f"Error actualizando perfil: {e}")
            default_avatar = QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'default_avatar.svg'))
            self.profile_pic.setPixmap(default_avatar.pixmap(32, 32))
            self.profile_name.setText("Error al cargar perfil")

    def _show_profile_menu(self, event):
        menu = QMenu(self)
        logout_action = menu.addAction("Cerrar Sesión")
        logout_action.triggered.connect(lambda: self.logoutRequested.emit())
        menu.exec(self.profile_pic.mapToGlobal(event.pos()))

    def _handle_search(self):
        """Maneja la búsqueda de eventos"""
        query = self.search_box.text().strip()
        if query:
            self.searchRequested.emit(query)
            # El widget de resultados se mostrará bajo la barra de búsqueda
            if hasattr(self.parent(), 'search_results_widget'):
                self.parent().search_results_widget.show_under_widget(self.search_box)
