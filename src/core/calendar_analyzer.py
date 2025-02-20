import requests
import json
from datetime import datetime, date, timedelta
import calendar
from utils.logger import logger
from models.event import Event
from typing import Dict, Any
from core.ai_assistant import AIAssistant
from config.settings import Settings

class CalendarAnalyzer:
    def __init__(self, calendar_manager=None, db_manager=None):
        self.calendar_manager = calendar_manager
        self.db_manager = db_manager
        self.settings = Settings()  # Inicializar Settings
        self.api_url = 'https://magicloops.dev/api/loop/b3dab971-9034-4bf6-93ad-4c701def8f33/run'
        self.analysis_event_title = 'Análisis Mensual de Eventos'
        self.ai_assistant = AIAssistant(db_manager)
        logger.info("CalendarAnalyzer inicializado con configuración")

    def _process_api_response(self, response_text: str) -> Dict[str, Any]:
        """Procesa la respuesta de la API y genera resumen usando IA"""
        try:
            logger.info("Procesando respuesta de API...")
            
            # Extraer JSON y Analysis
            parts = response_text.split("\n\nAnalysis:\n\n")
            json_part = parts[0].strip()
            analysis_part = parts[1].split("\n\nDEBUG:")[0].strip() if len(parts) > 1 else ""
            
            logger.debug("JSON extraído de la respuesta")
            
            # Parsear JSON
            json_data = json.loads(json_part)
            logger.info(f"JSON parseado exitosamente. Encontradas {len(json_data.get('predictions', []))} predicciones")
            
            # Generar resumen con IA
            logger.info("Generando resumen con DeepSeek...")
            prompt = f"""
            Analiza estas predicciones y genera un resumen claro en español.
            Enfócate en las predicciones más relevantes, sus probabilidades y posibles impactos.
            
            Predicciones:
            {json.dumps(json_data, indent=2, ensure_ascii=False)}
            """
            
            ai_summary = self.ai_assistant.process_message(prompt)
            logger.info("Resumen de IA generado exitosamente")
            
            # Combinar resumen y análisis original
            full_analysis = f"{ai_summary}\n\nAnalysis:\n{analysis_part}"
            
            return {
                "analysis": full_analysis,
                "timestamp": datetime.now().isoformat(),
                "predictions_count": len(json_data.get("predictions", []))
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear JSON de la API: {str(e)}")
            logger.debug(f"JSON que causó el error: {json_part}")
            raise
        except Exception as e:
            logger.error(f"Error procesando respuesta de API: {str(e)}")
            logger.debug(f"Respuesta que causó el error: {response_text[:500]}...")  # Primeros 500 caracteres
            raise

    def get_predictions(self) -> str:
        """Obtiene predicciones, ya sea de la API real o simulada"""
        try:
            if self.settings.use_mock_api:
                logger.info("Usando API simulada para predicciones")
                return self.settings.mock_api_response
            else:
                logger.info("Usando API real para predicciones")
                # Aquí iría la lógica de la API real
                return self._get_real_predictions()

        except Exception as e:
            logger.error(f"Error obteniendo predicciones: {str(e)}", exc_info=True)
            raise

    def _get_real_predictions(self):
        """Obtiene predicciones de la API real"""
        try:
            logger.info("Solicitando predicciones a API real...")
            response = requests.get(self.api_url)
            response.raise_for_status()
            
            # Esperar y obtener la respuesta
            api_response = response.text
            logger.info("Respuesta recibida de API real")
            
            return api_response
            
        except Exception as e:
            logger.error(f"Error obteniendo predicciones de API real: {str(e)}")
            raise

    def process_with_ai(self, api_response: str) -> Dict[str, Any]:
        """Procesa la respuesta de la API con IA"""
        try:
            logger.info("Iniciando process_with_ai")
            
            # Procesar con IA primero
            logger.info("Preparando llamada a DeepSeek...")
            prompt = f"Analiza estas predicciones y genera un resumen claro en español:\n{api_response}"
            
            ai_response = self.ai_assistant.process_message(prompt)
            logger.info("Respuesta de DeepSeek recibida")
            
            # Extraer el análisis usando la nueva función
            def extract_analysis(text):
                lines = text.split('\n')
                start_index = -1
                end_index = -1
                
                for i, line in enumerate(lines):
                    if line.strip() == "Analysis:":
                        start_index = i
                    elif line.strip() == "DEBUG:":
                        end_index = i
                        break
                
                if start_index != -1 and end_index != -1:
                    analysis_text = '\n'.join(lines[start_index + 1:end_index])
                    return analysis_text.strip()
                else:
                    logger.warning("No se encontraron los marcadores exactos en la respuesta de la API")
                    return api_response.strip()
            
            analysis_text = extract_analysis(api_response)
            
            return {
                'ai_analysis': ai_response,
                'api_analysis': analysis_text
            }
            
        except Exception as e:
            logger.error(f"Error en process_with_ai: {str(e)}")
            logger.error("Stack trace:", exc_info=True)
            raise

    def save_to_calendar(self, analysis_result: Dict[str, str]):
        """Guarda los resultados en el calendario"""
        try:
            logger.info("Guardando resultados en el calendario")
            
            # Obtener el último día del mes actual
            today = datetime.now()
            last_day = calendar.monthrange(today.year, today.month)[1]
            event_date = date(today.year, today.month, last_day)
            
            # Formatear descripción con ambos análisis
            description = f"{analysis_result['ai_analysis']}\n\n\nAnálisis:\n{analysis_result['api_analysis']}"
            
            event_data = {
                'summary': self.analysis_event_title,
                'description': description,
                'start': {
                    'date': event_date.isoformat()
                },
                'end': {
                    'date': (event_date + timedelta(days=1)).isoformat()
                }
            }
            
            # Eliminar evento anterior si existe
            self._delete_previous_analysis()
            
            # Crear nuevo evento
            self.calendar_manager.create_event(event_data)
            logger.info("Evento de análisis creado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando en calendario: {str(e)}", exc_info=True)
            raise

    def analyze_events(self) -> str:
        """Método completo que ejecuta todo el proceso"""
        try:
            # 1. Obtener predicciones
            logger.info("Iniciando obtención de predicciones desde API externa...")
            api_response = self.get_predictions()
            logger.info("Predicciones recibidas exitosamente")
            logger.debug(f"Respuesta de API: {api_response[:200]}...")  # Log primeros 200 caracteres
            
            # 2. Procesar con IA
            logger.info("Iniciando procesamiento con IA...")
            analysis_result = self.process_with_ai(api_response)
            logger.info("Análisis de IA completado")
            
            # 3. Guardar en calendario
            logger.info("Guardando resultados en calendario...")
            self.save_to_calendar(analysis_result)
            logger.info("Proceso de análisis completado exitosamente")
            
            return "Predicciones analizadas y guardadas en el calendario."
            
        except Exception as e:
            logger.error(f"Error en análisis de eventos: {str(e)}")
            return f"Error al analizar eventos: {str(e)}"

    def _prepare_events_summary(self, events) -> str:
        """Prepara un resumen de eventos para la API"""
        summary = "Análisis de eventos del mes:\n"
        for event in events:
            summary += f"- {event.title} ({event.start_datetime})\n"
        return summary

    def _create_event_from_dict(self, event_data: dict) -> Event:
        """Crea una instancia de Event desde un diccionario"""
        event = Event()
        event.title = event_data['summary']
        event.description = event_data.get('description', '')
        
        # Convertir fechas
        start_date = datetime.fromisoformat(event_data['start']['date'])
        end_date = datetime.fromisoformat(event_data['end']['date'])
        
        # Ajustar zona horaria
        event.start_datetime = start_date.replace(tzinfo=datetime.now().astimezone().tzinfo)
        event.end_datetime = end_date.replace(tzinfo=datetime.now().astimezone().tzinfo)
        
        return event

    def _update_or_create_analysis_event(self, analysis_result):
        """Actualiza o crea el evento con el resultado del análisis"""
        try:
            # Obtener último día del mes
            today = date.today()
            _, last_day = calendar.monthrange(today.year, today.month)
            last_date = date(today.year, today.month, last_day)
            
            # Buscar y eliminar evento existente con el mismo título
            logger.info(f"Buscando eventos existentes con título '{self.analysis_event_title}'")
            events = self.calendar_manager.get_events()
            
            for event in events:
                if event.title == self.analysis_event_title:
                    logger.info(f"Eliminando evento existente con ID: {event.google_event_id}")
                    try:
                        self.calendar_manager.delete_event(event.google_event_id)
                    except Exception as e:
                        logger.error(f"Error eliminando evento existente: {str(e)}")
            
            # Crear nuevo evento
            event_data = {
                'summary': self.analysis_event_title,
                'description': analysis_result['analysis'],
                'start': {
                    'date': last_date.isoformat()
                },
                'end': {
                    'date': (last_date + timedelta(days=1)).isoformat()
                }
            }
            
            # Crear nuevo evento
            self.calendar_manager.create_event(event_data)
            logger.info(f"Nuevo evento de análisis creado para {last_date}")
                
        except Exception as e:
            logger.error(f"Error creando evento de análisis: {str(e)}")
            raise

    def _delete_previous_analysis(self):
        """Elimina el evento de análisis anterior si existe"""
        try:
            logger.info("Buscando evento de análisis anterior...")
            
            # Obtener eventos del último día del mes
            today = datetime.now()
            last_day = calendar.monthrange(today.year, today.month)[1]
            target_date = date(today.year, today.month, last_day)
            
            # Buscar eventos
            events = self.calendar_manager.get_events()
            
            # Filtrar eventos del último día con el título específico
            for event in events:
                # Convertir fecha de inicio a date si es datetime
                event_date = event.start_datetime.date() if hasattr(event.start_datetime, 'date') else event.start_datetime
                
                if (event_date == target_date and 
                    event.title == self.analysis_event_title):
                    logger.info(f"Eliminando evento de análisis anterior: {event.google_event_id}")
                    self.calendar_manager.delete_event(event.google_event_id)
                    return
                
            logger.info("No se encontró evento de análisis anterior en el último día del mes")
            
        except Exception as e:
            logger.warning(f"Error al intentar eliminar evento anterior: {str(e)}")
            pass 