import logging
import os
from datetime import datetime

# Definir constantes aquí en lugar de importarlas
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')

# Configurar logger
logger = logging.getLogger('CalendarAI')
logger.setLevel(logging.DEBUG)

# Crear directorio de logs si no existe
os.makedirs(LOG_DIRECTORY, exist_ok=True)

# Configurar handler para archivo
log_file = os.path.join(LOG_DIRECTORY, f'calendar_app_{datetime.now().strftime("%Y%m%d")}.log')
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(file_handler)

# Configurar handler para consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(console_handler)

def setup_logger():
    """Setup application loggers"""
    os.makedirs(LOG_DIRECTORY, exist_ok=True)
    
    # Configurar logger principal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console_handler)
    
    # Handler para archivo general
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)
    
    # Handler específico para eventos
    events_logger = logging.getLogger('events')
    events_handler = logging.FileHandler(os.path.join(LOG_DIRECTORY, 'events.log'))
    events_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    events_logger.addHandler(events_handler)
    
    return logger

logger = setup_logger()
events_logger = logging.getLogger('events') 