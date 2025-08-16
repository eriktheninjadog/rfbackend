import os
import os
import requests
import time
class OpenRouterClient:
    
    
    def _read_bearer_key(self) -> str:
        try:
            with open('/var/www/html/api/rfbackend/routerkey.txt', 'r') as f:
                return f.readline().strip()
        except FileNotFoundError:
            raise Exception("API key file not found")

    
    def __init__(self, api_key=None):
        self.api_key = api_key or self._read_bearer_key()
        if not self.api_key:
            raise ValueError("OpenRouter API key not provided and not found in environment variables")
        self.base_url = "https://openrouter.ai/api/v1"
        self.chat = ChatCompletions(self)


class ChatCompletions:
    def __init__(self, client):
        self.client = client
    
    def create(self, model, messages, max_tokens=None, temperature=None, **kwargs):
        url = f"{self.client.base_url}/chat/completions"
        headers = {
            "Authorization": self.client.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
        }
        
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
            
        if temperature is not None:
            payload["temperature"] = temperature
            
        for key, value in kwargs.items():
            payload[key] = value
            
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return OpenRouterResponse(response.json())


class OpenRouterResponse:
    def __init__(self, response_data):
        self.id = response_data.get("id")
        self.choices = [Choice(choice) for choice in response_data.get("choices", [])]
        self.usage = response_data.get("usage", {})
        

class Choice:
    def __init__(self, choice_data):
        self.message = Message(choice_data.get("message", {}))
        self.index = choice_data.get("index")
        self.finish_reason = choice_data.get("finish_reason")
        

class Message:
    def __init__(self, message_data):
        self.content = message_data.get("content", "")
        self.role = message_data.get("role", "")


def get_completion(model, system_message, message, max_tokens=None, temperature=0.7):
    """
    Creates an OpenRouterClient and gets completion from OpenRouter API.
    
    Args:
        model: The model to use for generation
        system_message: System message/instructions
        message: User message to generate completion for
        max_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature
        
    Returns:
        The text content of the response
    """
    client = OpenRouterClient()
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": message}
    ]
    
    response = client.chat.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    if response.choices:
        return response.choices[0].message.content
    return ""
    
    

def llm_match( text: str, pattern: str, model="amazon/nova-micro-v1"):
    """Improved pattern-aware matching with examples"""
    system_prompt = f"""
    你係粵語結構分析專家。判斷文本是否符合指定的粵語模式，只需答 YES 或 NO。
    
    常見模式示例:
    - "首先X": 句子以「首先」開始
    - "慢慢X": 「慢慢」後面直接跟動詞 (如 慢慢食)
    - "點樣X": 「點樣」後面直接跟動詞 (如 點樣做)
    
    當前模式要求: {pattern}
    """
    
    user_prompt = f"判斷文本是否符合上述模式:\n{text}"
    
    try:
        response_text = get_completion( model, system_prompt, user_prompt, max_tokens=3, temperature=0.1)
        return "YES" in response_text
    except Exception as e:
        print(f"⚠️ LLM error: {e}")
        print("⏳ Retrying with GPT-4 fallback in 3s...")
        time.sleep(3)
        return llm_match( text, pattern, "openai/gpt-4-turbo")
