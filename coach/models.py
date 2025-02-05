# models.py
from dataclasses import dataclass
from typing import List

@dataclass
class RolePlayScenario:
    name: str
    context: str
    roles: List[str]
    suggested_vocab: List[str]
    difficulty: str

@dataclass
class StudentState:
    name: str = None
    level: str = "初學者"
    error_count: int = 0
    vocabulary: set = None
    
    def __post_init__(self):
        if self.vocabulary is None:
            self.vocabulary = set()
