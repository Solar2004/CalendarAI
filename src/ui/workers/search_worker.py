from PyQt6.QtCore import QObject, pyqtSignal
from collections import defaultdict
import re

class SearchWorker(QObject):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, calendar_manager, query):
        super().__init__()
        self.calendar_manager = calendar_manager
        self.query = query
        self.search_index = defaultdict(list)

    def _tokenize(self, text):
        """Tokeniza y normaliza el texto para búsqueda"""
        # Convertir a minúsculas y eliminar caracteres especiales
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Dividir en tokens y eliminar duplicados
        return set(text.split())

    def _get_match_type(self, text, query):
        """
        Determina el tipo de coincidencia:
        0 = Coincidencia exacta de palabra
        1 = Coincidencia como parte de otra palabra
        2 = Sin coincidencia
        """
        text_lower = text.lower()
        query_lower = query.lower()
        
        # Buscar coincidencia exacta de palabra
        words = set(re.findall(r'\b\w+\b', text_lower))
        if query_lower in words:
            return 0
        # Buscar coincidencia como parte de palabra
        elif query_lower in text_lower:
            return 1
        return 2

    def search(self):
        try:
            events = self.calendar_manager.get_events(log_raw=False)
            query = self.query.lower()
            
            # Filtrar y clasificar eventos
            matching_events = []
            for event in events:
                title_match = self._get_match_type(event.title, query)
                desc_match = self._get_match_type(event.description or '', query)
                
                # Solo incluir si hay algún tipo de coincidencia
                if min(title_match, desc_match) < 2:
                    matching_events.append((event, title_match, desc_match))
            
            # Agrupar eventos idénticos manteniendo la mejor coincidencia
            event_groups = {}
            for event, title_match, desc_match in matching_events:
                key = (event.title, event.description or '')
                if key not in event_groups:
                    event_groups[key] = {
                        'events': [],
                        'title_match': title_match,
                        'desc_match': desc_match
                    }
                event_groups[key]['events'].append(event)
            
            # Preparar resultados
            search_results = []
            for (title, desc), group_info in event_groups.items():
                search_results.append({
                    'title': title,
                    'description': desc,
                    'count': len(group_info['events']),
                    'events': sorted(group_info['events'], key=lambda e: e.start_datetime),
                    'title_match': group_info['title_match'],
                    'desc_match': group_info['desc_match']
                })
            
            # Ordenar resultados por relevancia
            search_results.sort(key=lambda x: (
                x['title_match'],  # Primero por tipo de coincidencia en título
                x['desc_match'],   # Luego por tipo de coincidencia en descripción
                x['title'].lower() # Finalmente alfabéticamente
            ))
            
            self.finished.emit(search_results)
        except Exception as e:
            self.error.emit(str(e)) 