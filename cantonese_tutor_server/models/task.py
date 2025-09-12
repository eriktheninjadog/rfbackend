from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import json

@dataclass
class Task:
    id: str
    level: int
    scenario_template: str
    target_skills: List[str]
    target_vocabulary: List[str]
    complexity: str
    prerequisites: List[str] = None
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

@dataclass
class ConversationEntry:
    speaker: str
    message: str
    timestamp: str
    message_type: str = "normal"
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

@dataclass
class TaskSession:
    task_id: str
    level: int
    date: str
    scenario: str
    conversation: List[ConversationEntry]
    errors_corrected: List[Dict[str, Any]]
    vocabulary_used: List[str]
    task_completed: bool = False
    duration_minutes: int = 0
    
    def __post_init__(self):
        if not hasattr(self, 'conversation'):
            self.conversation = []
        if not hasattr(self, 'errors_corrected'):
            self.errors_corrected = []
        if not hasattr(self, 'vocabulary_used'):
            self.vocabulary_used = []

@dataclass
class TaskCreationRequest:
    level: int
    scenario_template: str
    target_skills: List[str]
    target_vocabulary: List[str]
    complexity: str
    prerequisites: List[str] = None
