from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

def get_dark_palette():
    palette = QPalette()
    
    # Set colors for dark theme
    palette.setColor(QPalette.ColorRole.Window, QColor(32, 33, 36))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Link, QColor(66, 133, 244))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(66, 133, 244))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)

    return palette

def get_light_palette():
    return QPalette()  # Default light palette 

class Theme:
    # Light theme colors
    LIGHT_BG = "#ffffff"
    LIGHT_SIDEBAR_BG = "#f8f9fa"
    LIGHT_TEXT = "#202124"
    LIGHT_SECONDARY_TEXT = "#5f6368"
    LIGHT_ACCENT = "#4f46e5"  # Color principal morado similar a BetterStack
    LIGHT_ACCENT_HOVER = "#4338ca"
    LIGHT_BORDER = "#e0e0e0"
    LIGHT_HOVER = "#f5f5f5"
    
    # Dark theme colors
    DARK_BG = "#121212"
    DARK_SIDEBAR_BG = "#1e1e1e"
    DARK_TEXT = "#e8eaed"
    DARK_SECONDARY_TEXT = "#9aa0a6"
    DARK_ACCENT = "#6366f1"  # Color principal morado similar a BetterStack
    DARK_ACCENT_HOVER = "#818cf8"
    DARK_BORDER = "#3c4043"
    DARK_HOVER = "#2d2d2d"
    
    # Current theme
    is_dark_mode = False
    
    # Colores de eventos de Google Calendar
    EVENT_COLORS = {
        "1": "#7986cb",  # Lavanda
        "2": "#33b679",  # Salvia
        "3": "#8e24aa",  # Uva
        "4": "#e67c73",  # Mandarina
        "5": "#f6bf26",  # Plátano
        "6": "#f4511e",  # Tangerina
        "7": "#039be5",  # Pavo real
        "8": "#616161",  # Grafito
        "9": "#3f51b5",  # Arándano
        "10": "#0b8043", # Basilisco
        "11": "#d50000", # Tomate
        # Colores por defecto
        "default": "#4285f4", # Azul
    }
    
    # Método para obtener el estilo de un evento según su color_id
    @classmethod
    def get_event_style(cls, color_id=None):
        """Devuelve el estilo CSS para un evento según su color_id"""
        if not color_id or color_id not in cls.EVENT_COLORS:
            color_id = "default"
            
        event_color = cls.EVENT_COLORS.get(color_id, cls.EVENT_COLORS["default"])
        
        # Crear un color más claro para el fondo (con transparencia)
        bg_color = f"{event_color}20"  # 20 es la opacidad en hexadecimal (12.5%)
        
        # Determinar el color del texto basado en el tema actual
        text_color = cls.DARK_TEXT if cls.is_dark_mode else cls.LIGHT_TEXT
        
        return f"""
            border-left: 4px solid {event_color};
            background-color: {bg_color};
            color: {text_color};
        """
    
    # Estilos para secciones de cabecera
    SECTION_HEADER_STYLE_LIGHT = """
        QLabel {
            font-weight: bold;
            font-size: 14px;
            color: #202124;
            padding: 5px 0;
        }
    """
    
    SECTION_HEADER_STYLE_DARK = """
        QLabel {
            font-weight: bold;
            font-size: 14px;
            color: #e8eaed;
            padding: 5px 0;
        }
    """
    
    SECTION_HEADER_STYLE = SECTION_HEADER_STYLE_LIGHT
    
    # Estilos para eventos de todo el día
    EVENT_ALL_DAY_STYLE_LIGHT = """
        QLabel {
            background-color: #e8f0fe;
            color: #1a73e8;
            border-left: 3px solid #1a73e8;
            border-radius: 4px;
            padding: 4px 8px;
            margin: 2px;
            font-size: 12px;
        }
    """
    
    EVENT_ALL_DAY_STYLE_DARK = """
        QLabel {
            background-color: #303134;
            color: #8ab4f8;
            border-left: 3px solid #8ab4f8;
            border-radius: 4px;
            padding: 4px 8px;
            margin: 2px;
            font-size: 12px;
        }
    """
    
    EVENT_ALL_DAY_STYLE = EVENT_ALL_DAY_STYLE_LIGHT
    
    # Estilos generales
    MAIN_WINDOW_STYLE_LIGHT = f"""
        QMainWindow, QWidget#centralwidget {{
            background-color: {LIGHT_BG};
            color: {LIGHT_TEXT};
        }}
    """
    
    MAIN_WINDOW_STYLE_DARK = f"""
        QMainWindow, QWidget#centralwidget {{
            background-color: {DARK_BG};
            color: {DARK_TEXT};
        }}
    """
    
    MAIN_WINDOW_STYLE = MAIN_WINDOW_STYLE_LIGHT
    
    # Estilos para la barra lateral
    SIDEBAR_STYLE_LIGHT = f"""
        QWidget {{
            background-color: {LIGHT_SIDEBAR_BG};
            color: {LIGHT_TEXT};
            border-right: 1px solid {LIGHT_BORDER};
        }}
        
        QPushButton {{
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            background-color: {LIGHT_BG};
            color: {LIGHT_TEXT};
        }}
        
        QPushButton:hover {{
            background-color: {LIGHT_HOVER};
        }}
        
        QLineEdit {{
            border: 1px solid {LIGHT_BORDER};
            border-radius: 20px;
            padding: 8px 12px;
            background-color: {LIGHT_BG};
        }}
        
        QLineEdit:focus {{
            border: 1px solid {LIGHT_ACCENT};
        }}
    """
    
    SIDEBAR_STYLE_DARK = f"""
        QWidget {{
            background-color: {DARK_SIDEBAR_BG};
            color: {DARK_TEXT};
            border-right: 1px solid {DARK_BORDER};
        }}
        
        QPushButton {{
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            background-color: {DARK_BG};
            color: {DARK_TEXT};
        }}
        
        QPushButton:hover {{
            background-color: {DARK_HOVER};
        }}
        
        QLineEdit {{
            border: 1px solid {DARK_BORDER};
            border-radius: 20px;
            padding: 8px 12px;
            background-color: {DARK_BG};
            color: {DARK_TEXT};
        }}
        
        QLineEdit:focus {{
            border: 1px solid {DARK_ACCENT};
        }}
    """
    
    SIDEBAR_STYLE = SIDEBAR_STYLE_LIGHT
    
    # Estilos para botones de acción rápida
    QUICK_ACTION_BUTTON_STYLE_LIGHT = f"""
        QPushButton {{
            background-color: {LIGHT_BG};
            color: {LIGHT_TEXT};
            border: 1px solid {LIGHT_BORDER};
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {LIGHT_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {LIGHT_BORDER};
        }}
        QPushButton:disabled {{
            color: {LIGHT_SECONDARY_TEXT};
            background-color: {LIGHT_HOVER};
        }}
    """
    
    QUICK_ACTION_BUTTON_STYLE_DARK = f"""
        QPushButton {{
            background-color: {DARK_BG};
            color: {DARK_TEXT};
            border: 1px solid {DARK_BORDER};
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {DARK_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {DARK_BORDER};
        }}
        QPushButton:disabled {{
            color: {DARK_SECONDARY_TEXT};
            background-color: {DARK_HOVER};
        }}
    """
    
    QUICK_ACTION_BUTTON_STYLE = QUICK_ACTION_BUTTON_STYLE_LIGHT
    
    # Estilos para botones principales
    PRIMARY_BUTTON_STYLE_LIGHT = f"""
        QPushButton {{
            background-color: {LIGHT_ACCENT};
            color: white;
            border: none;
        border-radius: 4px;
            padding: 10px 20px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {LIGHT_ACCENT_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {LIGHT_ACCENT};
        }}
        QPushButton:disabled {{
            background-color: #c1c1c1;
        }}
    """
    
    PRIMARY_BUTTON_STYLE_DARK = f"""
        QPushButton {{
            background-color: {DARK_ACCENT};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 10px 20px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {DARK_ACCENT_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {DARK_ACCENT};
        }}
        QPushButton:disabled {{
            background-color: #505050;
            color: #a0a0a0;
        }}
    """
    
    PRIMARY_BUTTON_STYLE = PRIMARY_BUTTON_STYLE_LIGHT
    
    # Estilos para botones de navegación
    BUTTON_STYLE_LIGHT = f"""
        QPushButton {{
            background-color: {LIGHT_BG};
            color: {LIGHT_TEXT};
            border: 1px solid {LIGHT_BORDER};
            border-radius: 4px;
            padding: 6px 12px;
        }}
        QPushButton:hover {{
            background-color: {LIGHT_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {LIGHT_BORDER};
        }}
    """
    
    BUTTON_STYLE_DARK = f"""
        QPushButton {{
            background-color: {DARK_BG};
            color: {DARK_TEXT};
            border: 1px solid {DARK_BORDER};
            border-radius: 4px;
            padding: 6px 12px;
        }}
        QPushButton:hover {{
            background-color: {DARK_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {DARK_BORDER};
        }}
    """
    
    BUTTON_STYLE = BUTTON_STYLE_LIGHT
    
    # Estilos para mensajes de chat
    CHAT_MESSAGE_USER_STYLE_LIGHT = f"""
        QLabel {{
            background-color: {LIGHT_ACCENT};
            color: white;
            border-radius: 12px;
            padding: 8px 12px;
            margin: 4px;
            font-size: 13px;
        }}
    """
    
    CHAT_MESSAGE_USER_STYLE_DARK = f"""
        QLabel {{
            background-color: {DARK_ACCENT};
            color: white;
            border-radius: 12px;
            padding: 8px 12px;
            margin: 4px;
            font-size: 13px;
        }}
    """
    
    CHAT_MESSAGE_USER_STYLE = CHAT_MESSAGE_USER_STYLE_LIGHT
    
    CHAT_MESSAGE_AI_STYLE_LIGHT = f"""
        QLabel {{
            background-color: {LIGHT_HOVER};
            color: {LIGHT_TEXT};
            border-radius: 12px;
            padding: 8px 12px;
            margin: 4px;
            font-size: 13px;
        }}
    """
    
    CHAT_MESSAGE_AI_STYLE_DARK = f"""
        QLabel {{
            background-color: {DARK_HOVER};
            color: {DARK_TEXT};
            border-radius: 12px;
            padding: 8px 12px;
            margin: 4px;
            font-size: 13px;
        }}
    """
    
    CHAT_MESSAGE_AI_STYLE = CHAT_MESSAGE_AI_STYLE_LIGHT
    
    CHAT_TIMESTAMP_STYLE_LIGHT = f"""
        QLabel {{
            color: {LIGHT_SECONDARY_TEXT};
            font-size: 10px;
            background: transparent;
        }}
    """
    
    CHAT_TIMESTAMP_STYLE_DARK = f"""
        QLabel {{
            color: {DARK_SECONDARY_TEXT};
            font-size: 10px;
            background: transparent;
        }}
    """
    
    CHAT_TIMESTAMP_STYLE = CHAT_TIMESTAMP_STYLE_LIGHT
    
    # Estilos para scrollbars
    SCROLLBAR_STYLE_LIGHT = """
        QScrollBar:vertical {
            border: none;
            background: #f5f5f5;
            width: 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #c1c1c1;
            min-height: 30px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical:hover {
            background: #a0a0a0;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        
        QScrollBar:horizontal {
            border: none;
            background: #f5f5f5;
            height: 8px;
            margin: 0px;
        }
        QScrollBar::handle:horizontal {
            background: #c1c1c1;
            min-width: 30px;
            border-radius: 4px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #a0a0a0;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: none;
        }
    """
    
    SCROLLBAR_STYLE_DARK = """
        QScrollBar:vertical {
            border: none;
            background: #2d2d2d;
            width: 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #5f6368;
            min-height: 30px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical:hover {
            background: #7d7e80;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        
        QScrollBar:horizontal {
            border: none;
            background: #2d2d2d;
            height: 8px;
            margin: 0px;
        }
        QScrollBar::handle:horizontal {
            background: #5f6368;
            min-width: 30px;
            border-radius: 4px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #7d7e80;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: none;
        }
    """
    
    SCROLLBAR_STYLE = SCROLLBAR_STYLE_LIGHT
    
    # Estilos para eventos
    EVENT_TIMED_STYLE_LIGHT = f"""
        background-color: #e8f0fe;
        color: {LIGHT_ACCENT};
        border-left: 3px solid {LIGHT_ACCENT};
        border-radius: 4px;
        padding: 4px 8px;
        margin: 2px;
        font-size: 12px;
    """
    
    EVENT_TIMED_STYLE_DARK = f"""
        background-color: #303134;
        color: {DARK_ACCENT};
        border-left: 3px solid {DARK_ACCENT};
            border-radius: 4px;
            padding: 4px 8px;
            margin: 2px;
            font-size: 12px;
        """
    
    EVENT_TIMED_STYLE = EVENT_TIMED_STYLE_LIGHT
    
    # Método para cambiar entre temas
    @classmethod
    def toggle_theme(cls):
        cls.is_dark_mode = not cls.is_dark_mode
        
        # Actualizar estilos
        if cls.is_dark_mode:
            cls.MAIN_WINDOW_STYLE = cls.MAIN_WINDOW_STYLE_DARK
            cls.SIDEBAR_STYLE = cls.SIDEBAR_STYLE_DARK
            cls.QUICK_ACTION_BUTTON_STYLE = cls.QUICK_ACTION_BUTTON_STYLE_DARK
            cls.PRIMARY_BUTTON_STYLE = cls.PRIMARY_BUTTON_STYLE_DARK
            cls.BUTTON_STYLE = cls.BUTTON_STYLE_DARK
            cls.CHAT_MESSAGE_USER_STYLE = cls.CHAT_MESSAGE_USER_STYLE_DARK
            cls.CHAT_MESSAGE_AI_STYLE = cls.CHAT_MESSAGE_AI_STYLE_DARK
            cls.CHAT_TIMESTAMP_STYLE = cls.CHAT_TIMESTAMP_STYLE_DARK
            cls.SCROLLBAR_STYLE = cls.SCROLLBAR_STYLE_DARK
            cls.EVENT_TIMED_STYLE = cls.EVENT_TIMED_STYLE_DARK
            cls.SECTION_HEADER_STYLE = cls.SECTION_HEADER_STYLE_DARK
            cls.EVENT_ALL_DAY_STYLE = cls.EVENT_ALL_DAY_STYLE_DARK
        else:
            cls.MAIN_WINDOW_STYLE = cls.MAIN_WINDOW_STYLE_LIGHT
            cls.SIDEBAR_STYLE = cls.SIDEBAR_STYLE_LIGHT
            cls.QUICK_ACTION_BUTTON_STYLE = cls.QUICK_ACTION_BUTTON_STYLE_LIGHT
            cls.PRIMARY_BUTTON_STYLE = cls.PRIMARY_BUTTON_STYLE_LIGHT
            cls.BUTTON_STYLE = cls.BUTTON_STYLE_LIGHT
            cls.CHAT_MESSAGE_USER_STYLE = cls.CHAT_MESSAGE_USER_STYLE_LIGHT
            cls.CHAT_MESSAGE_AI_STYLE = cls.CHAT_MESSAGE_AI_STYLE_LIGHT
            cls.CHAT_TIMESTAMP_STYLE = cls.CHAT_TIMESTAMP_STYLE_LIGHT
            cls.SCROLLBAR_STYLE = cls.SCROLLBAR_STYLE_LIGHT
            cls.EVENT_TIMED_STYLE = cls.EVENT_TIMED_STYLE_LIGHT
            cls.SECTION_HEADER_STYLE = cls.SECTION_HEADER_STYLE_LIGHT
            cls.EVENT_ALL_DAY_STYLE = cls.EVENT_ALL_DAY_STYLE_LIGHT
        
        return cls.is_dark_mode
