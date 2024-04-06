
import requests
import json

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": f"Bearer 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",
    "HTTP-Referer": f"chinese.eriktamm.com", # Optional, for including your app on openrouter.ai rankings.
    "X-Title": f"chinese_app", # Optional. Shows in rankings on openrouter.ai.
  },
  data=json.dumps({
    "model": "anthropic/claude-3-opus", # Optional
    "messages": [
      {"role": "user", "content": "What is the meaning of life?"}
    ]
  })
)

json = response.json()
print(str(json))