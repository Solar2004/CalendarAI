from datetime import datetime
from typing import Dict, Any

class BaseModel:
    def __init__(self):
        self.id: int = None
        self.created_at: datetime = None
        self.updated_at: datetime = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model from dictionary"""
        instance = cls()
        instance.id = data.get('id')
        instance.created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        instance.updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        return instance 