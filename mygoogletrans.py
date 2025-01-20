#googletrans.py

from googletrans import Translator

def translate_to_chinese(text):
    try:
        translator = Translator()
        translation = translator.translate(text, dest='zh-cn')
        return translation.text
    except Exception as e:
        return f"Translation error: {str(e)}"

# Usage
text = "Hello, how are you?"
chinese_text = translate_to_chinese(text)
print(chinese_text)

