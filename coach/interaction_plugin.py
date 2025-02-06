#interaction_plugin.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class InteractionPlugin(ABC):
    @abstractmethod
    def get_input(self, prompt: str) -> str:
        """Get user input with optional prompt"""
        pass

    @abstractmethod
    def output_response(self, response: str) -> None:
        """Output system response to user"""
        pass

    @abstractmethod
    def start_session(self, initial_message: str) -> None:
        """Handle session initialization"""
        pass

    @abstractmethod
    def exit_session(self, final_message: str) -> None:
        """Handle session termination"""
        pass

    @abstractmethod
    def get_context(self) -> Dict[str, Any]:
        """Get any additional context needed for interaction"""
        pass
