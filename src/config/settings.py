import os
from dotenv import load_dotenv
import json
import logging
from PyQt6.QtCore import QObject, pyqtSignal

load_dotenv()

# Google Calendar API settings
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/calendar.db')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

class Settings(QObject):
    settingsChanged = pyqtSignal()  # Signal para notificar cambios

    def __init__(self):
        super().__init__()
        self.use_mock_api = False
        self.mock_api_response = ""
        self.auto_refresh_enabled = True
        self.load()  # Cargar configuración al inicializar

    def load(self):
        """Carga la configuración desde el archivo settings.json"""
        try:
            settings_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    data = json.load(f)
                    self.use_mock_api = data.get('use_mock_api', False)
                    self.mock_api_response = data.get('mock_api_response', "")
                    self.auto_refresh_enabled = data.get('auto_refresh_enabled', True)
                logging.info("Settings loaded successfully")
                self.settingsChanged.emit()  # Emitir señal cuando se cargan cambios
        except Exception as e:
            logging.error(f"Error loading settings: {e}")

    def save(self):
        """Guarda la configuración actual en el archivo settings.json"""
        try:
            settings_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'settings.json')
            os.makedirs(os.path.dirname(settings_path), exist_ok=True)
            
            with open(settings_path, 'w') as f:
                json.dump({
                    'use_mock_api': self.use_mock_api,
                    'mock_api_response': self.mock_api_response,
                    'auto_refresh_enabled': self.auto_refresh_enabled
                }, f, indent=4)
            logging.info("Settings saved successfully")
            self.settingsChanged.emit()  # Emitir señal cuando se guardan cambios
        except Exception as e:
            logging.error(f"Error saving settings: {e}")

    def load_from_file(self):
        # ... código para cargar configuración desde archivo ...
        pass

    def save_to_file(self):
        # ... código para guardar configuración a archivo ...
        pass
