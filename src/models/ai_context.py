from datetime import datetime
from typing import Dict, Any
from .base_model import BaseModel

class AIContext(BaseModel):
    def __init__(self):
        super().__init__()
        self.title: str = None
        self.content: str = None
        self.is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'title': self.title,
            'content': self.content,
            'is_active': self.is_active
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIContext':
        instance = super().from_dict(data)
        instance.title = data.get('title')
        instance.content = data.get('content')
        instance.is_active = data.get('is_active', True)
        return instance 