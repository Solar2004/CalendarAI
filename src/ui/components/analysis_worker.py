from PyQt6.QtCore import QThread, pyqtSignal
from utils.logger import logger
from typing import Optional

class AnalysisWorker(QThread):
    statusUpdated = pyqtSignal(str)  # Para actualizar el estado
    finished = pyqtSignal(str)  # Para el resultado final
    error = pyqtSignal(str)  # Para errores
    
    def __init__(self, calendar_analyzer):
        super().__init__()
        self.calendar_analyzer = calendar_analyzer
        self._is_running = False
        self._current_step = None
        
    def stop(self):
        """Detiene el proceso de análisis"""
        self._is_running = False
        logger.info("Deteniendo worker de análisis...")

    def _update_status(self, status: str):
        """Actualiza el estado y emite la señal"""
        logger.info(f"Estado: {status}")
        self.statusUpdated.emit(status)
        self._current_step = status

    def _execute_step(self, step_name: str, func, *args) -> Optional[any]:
        """Ejecuta un paso del proceso con manejo de errores"""
        try:
            self._update_status(f"Ejecutando: {step_name}")
            result = func(*args)
            logger.info(f"Paso completado: {step_name}")
            return result
        except Exception as e:
            logger.error(f"Error en {step_name}: {str(e)}", exc_info=True)
            raise

    def run(self):
        """Ejecuta el proceso de análisis"""
        self._is_running = True
        try:
            logger.info("=== Iniciando proceso de análisis ===")
            
            # 1. Obtener predicciones
            api_response = self._execute_step(
                "Obtención de predicciones",
                self.calendar_analyzer.get_predictions
            )
            if not self._is_running:
                return
            
            # 2. Procesar con IA
            analysis_result = self._execute_step(
                "Procesamiento con IA",
                self.calendar_analyzer.process_with_ai,
                api_response
            )
            if not self._is_running:
                return
            
            # 3. Guardar en calendario
            self._execute_step(
                "Guardado en calendario",
                self.calendar_analyzer.save_to_calendar,
                analysis_result
            )
            if not self._is_running:
                return
            
            logger.info("=== Proceso completado exitosamente ===")
            self.finished.emit("Análisis completado exitosamente")
            
        except Exception as e:
            logger.error("!!! Error en proceso de análisis !!!")
            logger.error(f"Error en paso '{self._current_step}': {str(e)}")
            self.error.emit(f"Error en {self._current_step}: {str(e)}")
        finally:
            self._is_running = False 