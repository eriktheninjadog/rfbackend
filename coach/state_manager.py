#state_manager.py
import json
import os

from typing import List, Dict
from models import StudentState

class StateManager:
    @staticmethod
    def save_state(student_state: StudentState, conversation_history: List[Dict]):
        state = {
            "student_level": student_state.level,
            "conversation_history": conversation_history,
            "error_count": student_state.error_count,
            "student_name": student_state.name,
            "vocabulary": list(student_state.vocabulary)
        }
        with open("student_state.json", "w") as f:
            json.dump(state, f)

    @staticmethod
    def load_state() -> tuple[StudentState, List[Dict]]:
        if not os.path.exists("student_state.json"):
            return StudentState(), []
            
        with open("student_state.json", "r") as f:
            state = json.load(f)
            student_state = StudentState(
                name=state.get("student_name"),
                level=state.get("student_level", "初學者"),
                error_count=state.get("error_count", 0),
                vocabulary=set(state.get("vocabulary", []))
            )
            conversation_history = state.get("conversation_history", [])
            return student_state, conversation_history

