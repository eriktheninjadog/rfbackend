from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from datetime import datetime
import json

@dataclass
class CompletedTask:
    task_id: str
    completion_date: str
    level: int
    duration_minutes: int = 0

@dataclass
class ErrorPattern:
    pattern: str
    error_type: str
    occurrences: int
    last_seen: str
    mastery_level: str = "learning"
    
@dataclass
class UserProgress:
    current_level: int = 1
    completed_tasks: List[CompletedTask] = None
    total_sessions: int = 0
    last_session: str = ""
    
    def __post_init__(self):
        if self.completed_tasks is None:
            self.completed_tasks = []

@dataclass
class UserData:
    progress: UserProgress
    error_patterns: Dict[str, ErrorPattern] = None
    vocabulary_used: List[str] = None
    
    def __post_init__(self):
        if self.error_patterns is None:
            self.error_patterns = {}
        if self.vocabulary_used is None:
            self.vocabulary_used = []
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        progress_data = data.get('progress', {})
        progress = UserProgress(
            current_level=progress_data.get('current_level', 1),
            completed_tasks=[CompletedTask(**task) for task in progress_data.get('completed_tasks', [])],
            total_sessions=progress_data.get('total_sessions', 0),
            last_session=progress_data.get('last_session', '')
        )
        
        error_patterns = {k: ErrorPattern(**v) for k, v in data.get('error_patterns', {}).items()}
        
        return cls(
            progress=progress,
            error_patterns=error_patterns,
            vocabulary_used=data.get('vocabulary_used', [])
        )
