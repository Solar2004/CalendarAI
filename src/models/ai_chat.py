from datetime import datetime
from typing import Dict, Any, Optional
from .base_model import BaseModel

class AIChat(BaseModel):
    def __init__(self):
        super().__init__()
        self.user_message: str = None
        self.ai_response: str = None
        self.context_id: Optional[int] = None
        self.action_taken: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'user_message': self.user_message,
            'ai_response': self.ai_response,
            'context_id': self.context_id,
            'action_taken': self.action_taken
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIChat':
        instance = super().from_dict(data)
        instance.user_message = data.get('user_message')
        instance.ai_response = data.get('ai_response')
        instance.context_id = data.get('context_id')
        instance.action_taken = data.get('action_taken')
        return instance 