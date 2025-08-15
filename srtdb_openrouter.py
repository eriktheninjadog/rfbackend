import os
import openai
import time

def init_openrouter():
    """Configure OpenAI client for OpenRouter"""
    return openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

def llm_match(client, text: str, pattern: str, model="amazon/nova-micro-v1"):
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
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=3,
            temperature=0.1
        )
        response_text = response.choices[0].message.content.strip().upper()
        return "YES" in response_text
    except Exception as e:
        print(f"⚠️ LLM error: {e}")
        print("⏳ Retrying with GPT-4 fallback in 3s...")
        time.sleep(3)
        return llm_match(client, text, pattern, "openai/gpt-4-turbo")
