from datetime import datetime
from typing import Dict, Any, Optional
from .base_model import BaseModel

class Event(BaseModel):
    def __init__(self, google_event: dict = None):
        super().__init__()
        if google_event:
            self.google_event_id = google_event.get('id')
            self.title = google_event.get('summary', 'Sin título')
            self.description = google_event.get('description', '')
            self.color_id = google_event.get('colorId')
            
            # Procesar fechas
            start = google_event.get('start', {})
            end = google_event.get('end', {})
            
            # Manejar eventos de todo el día y eventos con hora
            if 'date' in start:
                self.start_datetime = datetime.fromisoformat(start['date'])
                self.end_datetime = datetime.fromisoformat(end['date'])
            else:
                self.start_datetime = datetime.fromisoformat(start.get('dateTime', ''))
                self.end_datetime = datetime.fromisoformat(end.get('dateTime', ''))
            
            self.recurrence_rule = google_event.get('recurrence', [None])[0]
        else:
            self.google_event_id = None
            self.title = None
            self.description = None
            self.color_id = None
            self.start_datetime = None
            self.end_datetime = None
            self.recurrence_rule = None
        
        self.is_deleted = False

    def is_all_day(self) -> bool:
        """Determina si es un evento de todo el día"""
        if not self.start_datetime or not self.end_datetime:
            return False
        return (self.start_datetime.hour == 0 and
                self.end_datetime.hour == 23 and
                self.end_datetime.minute == 59)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'google_event_id': self.google_event_id,
            'title': self.title,
            'description': self.description,
            'color_id': self.color_id,
            'start_datetime': self.start_datetime.isoformat() if self.start_datetime else None,
            'end_datetime': self.end_datetime.isoformat() if self.end_datetime else None,
            'recurrence_rule': self.recurrence_rule,
            'is_deleted': self.is_deleted
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        event = cls()  # Crear instancia sin google_event
        event.google_event_id = data.get('google_event_id')
        event.title = data.get('title')
        event.description = data.get('description')
        event.color_id = data.get('color_id')
        event.start_datetime = datetime.fromisoformat(data['start_datetime']) if data.get('start_datetime') else None
        event.end_datetime = datetime.fromisoformat(data['end_datetime']) if data.get('end_datetime') else None
        event.recurrence_rule = data.get('recurrence_rule')
        event.is_deleted = data.get('is_deleted', False)
        return event 