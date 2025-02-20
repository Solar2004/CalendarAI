from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from utils.logger import logger
from models.event import Event
from .google_auth import GoogleAuthManager
import os
import json

class GoogleCalendarManager:
    def __init__(self, auth_manager: GoogleAuthManager):
        self.auth_manager = auth_manager
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize the Google Calendar service"""
        credentials = self.auth_manager.get_credentials()
        self.service = build('calendar', 'v3', credentials=credentials)

    def get_events(self, start_date: datetime = None, end_date: datetime = None) -> List[Event]:
        """Get events between dates"""
        try:
            if not start_date:
                start_date = datetime.now(timezone.utc)
            
            if not end_date:
                # Si no se especifica end_date, obtener todo el mes
                year = start_date.year
                month = start_date.month
                
                # Primer día del mes
                month_start = datetime(year, month, 1, tzinfo=timezone.utc)
                
                # Último día del mes siguiente (para asegurar eventos que cruzan meses)
                if month == 12:
                    next_month = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
                else:
                    next_month = datetime(year, month + 1, 1, tzinfo=timezone.utc)
                
                start_date = month_start
                end_date = next_month
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_date.isoformat(),
                timeMax=end_date.isoformat(),
                singleEvents=True,
                orderBy='startTime',
                maxResults=2500  # Aumentar límite para obtener más eventos
            ).execute()
            
            self._log_raw_events(events_result.get('items', []))
            
            events = events_result.get('items', [])
            
            # Guardar eventos raw solo si es una carga inicial
            if not start_date and not end_date:
                with open('logs/raw_events.json', 'w') as f:
                    json.dump(events, f, indent=2)
                logger.info("Raw events logged to logs/raw_events.json")

            return [self._convert_to_event(event) for event in events]
            
        except HttpError as error:
            logger.error(f'Error fetching events: {error}')
            return []

    def _log_raw_events(self, events: List[Dict]):
        """Log eventos en formato raw para debugging"""
        try:
            log_path = 'logs/raw_events.json'
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Raw events logged to {log_path}")
        except Exception as e:
            logger.error(f"Error logging raw events: {e}")

    def create_event(self, event_data: dict) -> Event:
        """Create a new event in Google Calendar"""
        try:
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event_data
            ).execute()
            
            # Convertir el evento creado a nuestro modelo
            return self._convert_to_event(created_event)
            
        except Exception as e:
            logger.error(f'Error creating event: {e}')
            raise

    def update_event(self, event_data: dict) -> Event:
        """Update an existing event"""
        try:
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_data['id'],
                body=event_data
            ).execute()
            
            return self._convert_to_event(updated_event)
            
        except Exception as e:
            logger.error(f'Error updating event: {e}')
            raise

    def delete_event(self, event_id: str):
        """Elimina un evento del calendario"""
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            logger.info(f"Evento eliminado: {event_id}")
        except Exception as e:
            logger.error(f"Error eliminando evento: {str(e)}")
            raise

    def _convert_to_event(self, google_event: Dict[str, Any]) -> Event:
        """Convert Google Calendar event to our Event model"""
        event = Event()
        event.google_event_id = google_event['id']
        event.title = google_event['summary']
        event.description = google_event.get('description', '')
        
        # Handle start time with timezone awareness
        start = google_event['start'].get('dateTime', google_event['start'].get('date'))
        if 'T' in start:  # Es un datetime
            event.start_datetime = datetime.fromisoformat(start.replace('Z', '+00:00'))
        else:  # Es una fecha
            event.start_datetime = datetime.strptime(start, '%Y-%m-%d').replace(
                hour=0, minute=0, second=0, tzinfo=timezone.utc
            )
        
        # Handle end time with timezone awareness
        end = google_event['end'].get('dateTime', google_event['end'].get('date'))
        if 'T' in end:  # Es un datetime
            event.end_datetime = datetime.fromisoformat(end.replace('Z', '+00:00'))
        else:  # Es una fecha
            event.end_datetime = datetime.strptime(end, '%Y-%m-%d').replace(
                hour=23, minute=59, second=59, tzinfo=timezone.utc
            )
        
        # Handle recurrence
        event.recurrence_rule = google_event.get('recurrence', [None])[0]
        
        return event

    def _convert_to_google_event(self, event: Event) -> Dict[str, Any]:
        """Convert our Event model to Google Calendar event format"""
        google_event = {
            'summary': event.title,
            'description': event.description or '',
            'start': {
                'dateTime': event.start_datetime.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': event.end_datetime.isoformat(),
                'timeZone': 'UTC',
            }
        }
        
        if event.recurrence_rule:
            google_event['recurrence'] = [event.recurrence_rule]
            
        return google_event 