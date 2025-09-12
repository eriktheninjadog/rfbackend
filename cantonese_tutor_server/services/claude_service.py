import requests
import json
from typing import Optional
from config import OPENROUTER_API_KEY, OPENROUTER_URL, MODEL_NAME

class ClaudeService:
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_URL
        self.model = MODEL_NAME
        
    def chat(self, messages: list, system_prompt: str = "") -> Optional[str]:
        """Send a chat request to Claude via OpenRouter"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://chinese.eriktamm.com",
            "X-Title": "Cantonese Tutor"
        }
        
        api_messages = []
        if system_prompt:
            api_messages.append({"role": "system", "content": system_prompt})
        
        api_messages.extend(messages)
        
        payload = {
            "model": self.model,
            "messages": api_messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            print(f"API請求錯誤: {e}")
            return None
        except (KeyError, IndexError) as e:
            print(f"回應解析錯誤: {e}")
            return None
    
    def get_tutor_response(self, conversation_history: list, system_context: str) -> Optional[str]:
        """Get a response from Claude in tutor mode"""
        
        system_prompt = f"""你係一個粵語老師，用直接教學法教學。規則：
1. 只用粵語溝通，絕對唔用英文或普通話
2. 學生犯錯就立即糾正，用引導式問題幫佢自己發現錯誤
3. 確保學生理解錯誤先至繼續主要任務
4. 推學生自己搵答案，唔好太快提供標準答案
5. 保持任務導向，幫學生解決問題

當前情況：{system_context}"""

        return self.chat(conversation_history, system_prompt)
