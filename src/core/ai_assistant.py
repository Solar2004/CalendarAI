import requests
import json
from typing import List, Dict, Any, Optional
from config.constants import OPENROUTER_API_KEY, APP_NAME, OPENROUTER_API_KEY
from utils.logger import logger
from models.ai_context import AIContext
from models.ai_chat import AIChat
from .database import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class AIAssistant:
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "google/gemini-2.0-flash-lite-preview-02-05:free"
        self.active_context = None
        self.conversation_history = []
        
        # Solo cargar el contexto si tenemos db_manager
        if self.db_manager:
            self._load_active_context()
            self.load_chat_history()

    def _load_active_context(self):
        """Load the active context from database"""
        try:
            query = "SELECT * FROM ai_context WHERE is_active = TRUE ORDER BY updated_at DESC LIMIT 1"
            results = self.db_manager.execute_query(query)
            if results:
                self.active_context = AIContext.from_dict(dict(results[0]))
        except Exception as e:
            logger.error(f"Error loading AI context: {str(e)}")

    def _make_api_request(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Make request to DeepSeek API"""
        try:
            # Formatear el cuerpo de la solicitud
            request_body = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": messages[-1]['content']  # Usar el último mensaje del historial
                            }
                        ]
                    }
                ]
            }

            response = requests.post(
                url=self.api_url,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",  # Usar la clave de API correcta
                    "Content-Type": "application/json",
                    "HTTP-Referer": "localhost",  # Update with your site URL
                    "X-Title": APP_NAME,
                },
                data=json.dumps(request_body)  # Usar el cuerpo formateado
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"AI API request failed: {str(e)}")
            raise

    async def get_response(self, message: str) -> str:
        """Obtiene respuesta de DeepSeek"""
        logger.info("Recibiendo mensaje del usuario: %s", message)
        
        # Agregar contexto del calendario
        prompt = "Eres un asistente de calendario inteligente. Ayudas a organizar, optimizar y analizar eventos y horarios.\n\n"

        # Incluir el historial de conversación
        if self.conversation_history:
            logger.debug("Historial de conversación antes de agregar el mensaje: %s", self.conversation_history)
            prompt += "Historial de conversación:\n"
            for entry in self.conversation_history[-20:]:  # Solo los últimos 20 mensajes
                role = "USER" if entry['role'] == 'user' else "IA"
                prompt += f"{role}: {entry['content']}\n"

        prompt += f"USER: {message}\n"
        logger.debug("Prompt enviado a la IA: %s", prompt)

        try:
            # Aquí iría la llamada real a DeepSeek
            response = "Respuesta de prueba del asistente"
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": response})
            logger.info("Respuesta de la IA: %s", response)
            return response
        except Exception as e:
            logger.error("Error al comunicarse con el asistente: %s", str(e))
            return f"Error al comunicarse con el asistente: {str(e)}"

    def process_message(self, message: str) -> str:
        """Procesa un mensaje y obtiene respuesta de DeepSeek"""
        try:
            logger.info("Iniciando procesamiento de mensaje en AIAssistant")
            
            if not OPENROUTER_API_KEY:
                logger.error("API key no configurada")
                return "Error: API key no configurada. Por favor, configura OPENROUTER_API_KEY en el archivo .env"

            logger.info("Preparando request a DeepSeek...")
            messages = self._prepare_messages(message)
            
            logger.debug("Enviando request a DeepSeek API...")
            try:
                response = requests.post(
                    url=self.api_url,
                    headers=self._get_headers(),
                    data=json.dumps({
                        "model": self.model,
                        "messages": messages
                    }),
                    timeout=30  # Timeout de 30 segundos
                )
                response.raise_for_status()
                logger.info("Respuesta recibida de DeepSeek")
                
            except requests.Timeout:
                logger.error("Timeout en request a DeepSeek")
                return "Error: Timeout en la comunicación con DeepSeek"
            except requests.RequestException as e:
                logger.error(f"Error en request a DeepSeek: {str(e)}")
                return f"Error en la comunicación con DeepSeek: {str(e)}"
                
            response_data = response.json()
            logger.debug("Datos de respuesta de la IA: %s", response_data)
            
            if 'choices' not in response_data:
                logger.error(f"Respuesta inesperada: {response_data}")
                return "Error: Respuesta inesperada de la API"
            
            ai_response = response_data['choices'][0]['message']['content']
            logger.info("Respuesta procesada exitosamente")
            
            self._update_conversation_history(message, ai_response)
            
            return ai_response

        except Exception as e:
            logger.error("Error crítico en process_message")
            logger.error(f"Tipo de error: {type(e).__name__}")
            logger.error(f"Error: {str(e)}")
            logger.error("Stack trace:", exc_info=True)
            return f"Error al procesar el mensaje: {str(e)}"

    def _save_chat(self, user_message: str, ai_response: str):
        """Guarda la conversación en la base de datos"""
        if not self.db_manager:
            logger.warning("No hay db_manager disponible, no se guardará el chat.")
            return  # No guardar si no hay db_manager
            
        try:
            query = """
                INSERT INTO ai_chat_history 
                (user_message, ai_response) 
                VALUES (?, ?)
            """
            self.db_manager.execute_update(query, (user_message, ai_response))
            logger.info("Chat guardado en la base de datos: %s", user_message)
        except Exception as e:
            logger.error(f"Error guardando chat: {str(e)}")

    def set_context(self, title: str, content: str):
        """Set new active context"""
        # Deactivate current active context
        if self.active_context:
            self.db_manager.execute_update(
                "UPDATE ai_context SET is_active = FALSE WHERE id = ?",
                (self.active_context.id,)
            )

        # Create new context
        query = """
            INSERT INTO ai_context (title, content, is_active)
            VALUES (?, ?, TRUE)
        """
        self.db_manager.execute_update(query, (title, content))
        self._load_active_context()

    def get_chat_history(self, limit: int = 50) -> List[AIChat]:
        """Get recent chat history"""
        query = """
            SELECT * FROM ai_chat_history 
            ORDER BY timestamp DESC 
            LIMIT ?
        """
        results = self.db_manager.execute_query(query, (limit,))
        return [AIChat.from_dict(dict(row)) for row in results]

    def _prepare_messages(self, message: str) -> List[Dict[str, str]]:
        """Prepara los mensajes para la API de DeepSeek"""
        # Mensaje del sistema
        system_message = {
            "role": "system",
            "content": """Eres un asistente de calendario inteligente. 
            Ayudas a organizar, optimizar y analizar eventos y horarios.
            Proporciona respuestas concisas y prácticas."""
        }
        
        # Mensaje del usuario
        user_message = {
            "role": "user",
            "content": message
        }
        
        # Combinar todo
        return [system_message] + self.conversation_history + [user_message]

    def _get_headers(self) -> Dict[str, str]:
        """Obtiene los headers para la API de DeepSeek"""
        return {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8080",
            "X-Title": APP_NAME,
        }

    def _update_conversation_history(self, message: str, ai_response: str):
        """Actualiza el historial de conversación"""
        logger.info("Actualizando historial de conversación")
        # Agregar mensajes al historial
        self.conversation_history.append({"role": "user", "content": message})
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        
        logger.debug("Historial de conversación actualizado: %s", self.conversation_history)

        # Mantener historial manejable (últimos 20 mensajes)
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        # Guardar en base de datos si está disponible
        if self.db_manager:
            self._save_chat(message, ai_response)

    def load_chat_history(self):
        """Carga el historial de chat desde la base de datos"""
        if not self.db_manager:
            logger.warning("No hay db_manager disponible, no se puede cargar el historial.")
            return

        try:
            query = "SELECT user_message, ai_response FROM ai_chat_history ORDER BY id DESC LIMIT 20"
            results = self.db_manager.execute_query(query)
            for user_message, ai_response in results:
                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append({"role": "assistant", "content": ai_response})
            logger.info("Historial de chat cargado exitosamente.")
        except Exception as e:
            logger.error(f"Error al cargar el historial de chat: {str(e)}") 