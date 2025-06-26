import requests
import json
import time
import re

import openrouter



def generate_article_game(article_text):
    """
    Calls the OpenRouter API to generate a Chinese learning game from an article.
    
    Args:
        api_key (str): Your OpenRouter API key
        article_text (str): The Chinese news article text
    
    Returns:
        dict: Parsed JSON response with game content
    """
    # API endpoint
    
    
    
    
    # Create the prompt with the article text
    prompt = f"""
    You are a Mandarin teaching assistant generating game content from this news article:

    ARTICLE: {article_text}

    Generate JSON containing:
    1. 5 cloze questions focusing on news terminology and grammar
    2. 3 sentence reconstruction challenges
    3. Terminology matching pairs (term:definition)
    4. All answers with explanations

    {{
      "article_metadata": {{
        "title": "...",
        "source": "...",
        "difficulty": "HSK4"
      }},
      "cloze_questions": [
        {{
          "sentence": "中国___宣布新的经济政策",
          "blank_index": 2,
          "options": ["政府", "公司", "学校"],
          "answer": 0,
          "explanation": "政府 (government) is the subject typically announcing policies"
        }}
      ],
      "sentence_reconstruction": {{
        "original": "外交部发言人回应了记者提问",
        "shuffled": ["提问", "回应了", "发言人", "外交部", "记者"],
        "hint": "Subject-verb-object structure"
      }},
      "terminology_pairs": [
        ["经济增长", "Economic growth"],
        ["通货膨胀", "Inflation"]
      ]
    }}
    """

    # Make the API request
    try:
        api = openrouter.OpenRouterAPI()
        content = api.open_router_claude_3_7_sonnet("You are Cantonese teacher",prompt)

        
        # Extract the JSON from the content
        # The API might return markdown-formatted JSON or raw JSON
        try:
            # Try to load the content directly
            game_data = json.loads(content)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from markdown
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', content)
            if json_match:
                json_str = json_match.group(1)
                game_data = json.loads(json_str)
            else:
                raise ValueError("Could not extract valid JSON from API response")
        
        # Validate the structure of the returned JSON
        required_keys = ["article_metadata", "cloze_questions", "sentence_reconstruction", "terminology_pairs"]
        for key in required_keys:
            if key not in game_data:
                raise ValueError(f"Missing required key '{key}' in generated content")
        
        return game_data
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error processing response: {e}")
        return None

# Example usage:
# api_key = "your_openrouter_api_key"
# article_text = "你的中文文章内容..."
# game = generate_article_game(api_key, article_text)
# if game:
#     print(json.dumps(game, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    # Example usage 
    article_text = "中国政府宣布新的经济政策，旨在促进经济增长和稳定市场。"
    game = generate_article_game( article_text)
    if game:
        print(json.dumps(game, ensure_ascii=False, indent=2))