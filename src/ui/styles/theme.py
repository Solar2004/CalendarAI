from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

def get_dark_palette():
    palette = QPalette()
    
    # Set colors for dark theme
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

    return palette

def get_light_palette():
    return QPalette()  # Default light palette 

class Theme:
    # Colores principales
    PRIMARY = "#1a73e8"  # Azul Google
    BACKGROUND = "#ffffff"
    TEXT_PRIMARY = "#3c4043"
    TEXT_SECONDARY = "#70757a"
    BORDER = "#dadce0"
    
    # Estilos comunes
    BUTTON_STYLE = """
        QPushButton {
            border: 1px solid #dadce0;
            border-radius: 4px;
            padding: 8px 16px;
            color: #3c4043;
            background: white;
        }
        QPushButton:hover {
            background: #f1f3f4;
        }
    """
    
    MENUBAR_STYLE = """
        QMenuBar {
            background-color: white;
            color: #3c4043;
        }
        QMenuBar::item:selected {
            background-color: #f1f3f4;
        }
        QMenu {
            background-color: white;
            color: #3c4043;
        }
        QMenu::item:selected {
            background-color: #f1f3f4;
        }
    """
    
    MAIN_WINDOW_STYLE = """
        QMainWindow {
            background-color: white;
        }
        QWidget {
            background-color: white;
            color: #3c4043;
        }
        QScrollArea {
            background-color: white;
            border: none;
        }
    """
    
    CALENDAR_CELL_STYLE = """
        background-color: white;
        color: #3c4043;
        border: 1px solid #dadce0;
    """
    
    EVENT_ALL_DAY_STYLE = """
        background-color: #e8f0fe;
        color: #1a73e8;
        border-radius: 2px;
        padding: 2px 4px;
    """
    
    EVENT_TIMED_STYLE = """
        background-color: #e8f0fe;
        color: #1a73e8;
        border-left: 3px solid #1a73e8;
        border-radius: 4px;
        padding: 4px 8px;
        margin: 2px;
        font-size: 12px;
    """
    
    HEADER_STYLE = """
        font-size: 24px;
        font-weight: bold;
        color: #3c4043;
        padding: 10px;
    """
    
    CHAT_INPUT_STYLE = """
        QTextEdit {
            border: 1px solid #dadce0;
            border-radius: 4px;
            padding: 8px;
            background: white;
            color: #3c4043;
        }
    """
    
    CHAT_MESSAGE_USER_STYLE = """
        QLabel {
            background-color: #1a73e8;
            color: white;
            border-radius: 12px;
            padding: 8px 12px;
            margin: 4px;
            font-size: 13px;
        }
    """
    
    CHAT_MESSAGE_AI_STYLE = """
        QLabel {
            background-color: #f1f3f4;
            color: #202124;
            border-radius: 12px;
            padding: 8px 12px;
            margin: 4px;
            font-size: 13px;
        }
    """
    
    CHAT_CONTAINER_STYLE = """
        QWidget {
            background-color: white;
            border: none;
        }
    """
    
    SIDEBAR_BACKGROUND = "#f8f9fa"  # Un gris muy claro
    
    SIDEBAR_STYLE = """
        QWidget {
            background-color: #f8f9fa;
            border-left: 1px solid #dadce0;
        }
        QScrollArea {
            background-color: #f8f9fa;
            border: none;
        }
    """
    
    ICON_BUTTON_STYLE = """
        QPushButton {
            border: 1px solid #dadce0;
            border-radius: 4px;
            padding: 4px;
            background: white;
            min-width: 32px;
            min-height: 32px;
        }
        QPushButton:hover {
            background: #f1f3f4;
        }
        QPushButton:pressed {
            background: #e8eaed;
        }
    """
    
    HOUR_LABEL_STYLE = """
        padding: 8px;
        color: #70757a;
        background-color: white;
        border-right: 1px solid #e0e0e0;
    """
    
    WEEK_CELL_STYLE = """
        background-color: white;
        border-bottom: 1px solid #e0e0e0;
        border-right: 1px solid #e0e0e0;
        min-height: 40px;
    """
    
    EVENT_WEEK_STYLE = """
        background-color: #e8f0fe;
        color: #1a73e8;
        border-radius: 4px;
        padding: 4px;
        margin: 2px;
        font-size: 11px;
    """
    
    SECTION_HEADER_STYLE = """
        font-weight: bold;
        color: #3c4043;
        padding: 8px 4px;
        font-size: 14px;
        background-color: white;
        border-bottom: 1px solid #e0e0e0;
    """
    
    HOUR_CELL_STYLE = """
        background-color: white;
        border-bottom: 1px solid #e0e0e0;
        min-height: 48px;
    """
    
    # Agregar estilos para scrollbars modernos
    SCROLLBAR_STYLE = """
        QScrollBar:vertical {
            border: none;
            background: #f8f9fa;
            width: 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #dadce0;
            border-radius: 4px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background: #bdc1c6;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
    """
    
    QUICK_ACTION_BUTTON_STYLE = """
        QPushButton {
            border: 1px solid #dadce0;
            border-radius: 16px;
            padding: 6px 12px;
            color: #1a73e8;
            background: #e8f0fe;
            font-size: 12px;
            min-width: 80px;
        }
        QPushButton:hover {
            background: #d2e3fc;
        }
        QPushButton:pressed {
            background: #c2d7f9;
        }
    """
    
    AI_BUTTON_STYLE = """
        QPushButton {
            border: 1px solid #dadce0;
            border-radius: 20px;
            padding: 8px 16px;
            color: #1a73e8;
            background: white;
            font-size: 13px;
        }
        QPushButton:hover {
            background: #f8f9fa;
            border-color: #1a73e8;
        }
    """
    
    # Colores para eventos según colorId de Google Calendar
    EVENT_COLORS = {
        "1": "#7986cb",  # Lavanda
        "2": "#33b679",  # Salvia
        "3": "#8e24aa",  # Uva
        "4": "#e67c73",  # Mandarina
        "5": "#f6c026",  # Girasol
        "6": "#f5511d",  # Tomate
        "7": "#039be5",  # Océano
        "8": "#616161",  # Grafito
        "9": "#3f51b5",  # Arándano
        "10": "#0b8043", # Basilisco
        "11": "#d60000", # Rubí
    }
    
    def get_event_style(color_id: str = None) -> str:
        """Genera el estilo para un evento basado en su colorId"""
        color = Theme.EVENT_COLORS.get(color_id, "#1a73e8")  # Color por defecto si no hay colorId
        return f"""
            background-color: {color}33;  /* Color con 20% de opacidad */
            color: {color};
            border-left: 3px solid {color};
            border-radius: 4px;
            padding: 4px 8px;
            margin: 2px;
            font-size: 12px;
        """ 