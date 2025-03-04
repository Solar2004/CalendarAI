import requests
import json
import logging
from core.ai_assistant import AIAssistant  # Importar AIAssistant para acceder a la configuración
from config.constants import OPENROUTER_API_KEY, APP_NAME

logger = logging.getLogger(__name__)

class FunctionIdentifier:
    def __init__(self):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.api_key = OPENROUTER_API_KEY

    def identify_function(self, message: str) -> str:
        """Identifica si el mensaje solicita una función específica."""
        prompt = f"""
        Eres una IA enfocada en identificar funciones en el mensaje del usuario. 
        El mensaje es: "{message}"
        Las funciones disponibles son:
        - codigo_morse: traduce el mensaje a código Morse
        - otra_funcion: descripción de otra función
        Asegúrate de devolver solo la ID de la función en minúsculas, o 'none' si no hay función.
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "google/gemini-2.0-flash-lite-preview-02-05:free",
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            response = requests.post(self.api_url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            response_data = response.json()
            function_id = response_data['choices'][0]['message']['content'].strip()
            logger.info("Función identificada: %s", function_id)
            return function_id
        except Exception as e:
            logger.error("Error al identificar la función: %s", str(e))
            return "none" 