# llm_service.py
import requests
import json
from typing import Dict, Any

class LLMService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def query(self, prompt: str, json_mode: bool = False) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek/v3",
            "messages": [{"role": "system", "content": prompt}],
            "temperature": 0.3 if json_mode else 0.7,
            "max_tokens": 500
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        response = requests.post(url, headers=headers, json=payload)
        return response.json()['choices'][0]['message']['content']

