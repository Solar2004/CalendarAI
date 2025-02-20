import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Application constants
APP_NAME = 'Calendar AI Assistant'
APP_VERSION = '0.1.0'

# UI constants
DEFAULT_WINDOW_SIZE = (1024, 768)
DEFAULT_FONT_SIZE = 12

# Theme constants
DARK_MODE_STYLE = """
    QMainWindow {
        background-color: #353535;
    }
    QWidget {
        color: #ffffff;
        background-color: #353535;
    }
    QMenuBar {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QMenuBar::item:selected {
        background-color: #3b3b3b;
    }
    QMenu {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QMenu::item:selected {
        background-color: #3b3b3b;
    }
    QToolBar {
        background-color: #2b2b2b;
        border: none;
    }
    QStatusBar {
        background-color: #2b2b2b;
        color: #ffffff;
    }
"""

# Database constants
DATABASE_NAME = 'calendar.db'
DATABASE_PATH = 'data/calendar.db'

# Logging constants
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DIRECTORY = 'logs'

# AI constants
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY no encontrada en variables de entorno")
DEFAULT_AI_CONTEXT = """
You are a helpful calendar assistant. You help users manage their schedule and create events.
You can understand natural language requests and convert them into structured event data.
Always be concise and focused on calendar-related tasks.
"""

# Google Calendar constants
GOOGLE_TOKEN_FILE = 'google_token.pickle'
