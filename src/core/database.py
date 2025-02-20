import sqlite3
from pathlib import Path
from utils.logger import logger

class DatabaseManager:
    def __init__(self):
        self.db_path = Path('data/calendar.db')
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_db()

    def init_db(self):
        """Inicializa la base de datos con las tablas necesarias"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # Tabla para el historial de chat
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_message TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    context_id INTEGER,
                    action_taken TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla para contextos de AI
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")

    def execute_query(self, query: str, params: tuple = None) -> list:
        """Ejecuta una consulta y retorna los resultados"""
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()

    def execute_update(self, query: str, params: tuple = None):
        """Ejecuta una actualización en la base de datos"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit() 