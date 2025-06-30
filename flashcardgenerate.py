#flashcardgenerate.py





import openrouter
import json
import re

def extract_json_from_text(text):
    """
    Extracts and parses a JSON block from within text.
    
    Args:
        text (str): Text containing a JSON block
        
    Returns:
        dict or list: Parsed JSON object or None if no valid JSON found
    """
    # Try to find JSON pattern (text between curly braces including nested structures)
    json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
    
    if json_match:
        try:
            # Extract the matched JSON string and parse it
            json_str = json_match.group(0)
            return json.loads(json_str)
        except json.JSONDecodeError:
            print("Found JSON-like structure but couldn't parse it")
            return None
    else:
        print("No JSON structure found in the text")
        return None


import hashlib
import random

def save_flashcards_to_json(flashcards, prefix="flashcard"):
    """
    Saves an array of flashcards to a JSON file with a random integer in the filename.
    
    Args:
        flashcards (list): Array of flashcard data to save
        prefix (str): Prefix for the filename (default: 'flashcard')
        
    Returns:
        str: The filename that was created
    """
    random_int = random.randint(1000, 9999)
    filename = f"{prefix}{random_int}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(flashcards, f, ensure_ascii=False, indent=2)
    
    return filename


import textprocessing
def generate_flashcards(text):    
    api = openrouter.OpenRouterAPI()
    result = api.open_router_nova_lite_v1("""
    split this text into the separate words and create a prompt for each one that is suitable to generate an image for the word that can be used in a flashcard game. Make the output in this json format [{"word":word,"sentence": the sentence the word is in in the structure,"prompt":prompt},...] Avoid words that are on HSK1-2 level. Here is the text:
    
    """+ text )
    flashcards = extract_json_from_text(result)
    for card in flashcards:
         md5signature = hashlib.md5(card['prompt'].encode('utf-8')).hexdigest()
         card['md5signature'] = md5signature
         card['tokens'] = textprocessing.split_text(card['sentence'])
         with open(md5signature + ".prompt", "w", encoding="utf-8") as f:
            f.write(card['prompt'])
    save_flashcards_to_json(flashcards, prefix="flashcard")
 



if __name__ == "__main__":
    trim = """
    
今日是《香港國安法》公布實施5周年，特區政府發言人表示，這是重要的日子，5年來《香港國安法》為香港實現由亂到治的重大轉折；為維護國家主權、安全和發展利益，奠定了堅實的法律基礎，更是「一國兩制」事業的重要里程碑。

發言人強調，維護國家安全只有進行時，沒有完成時。在地緣政治風險不斷升溫下，特區政府必定繼續在《香港國安法》和《維護國家安全條例》的堅實保障下，堅決維護國家主權、安全、發展利益，持續完善相關法律制度和執行機制，以更有效應對不斷變化的國安風險挑戰；以及深化宣傳教育，讓每位市民都自覺維護國家安全，從而形成抵禦外部干預的社會基礎，以高水平安全護航高質量發展，不斷譜寫「一國兩制」實踐新篇章。
　　
發言人說，國家安全是頭等大事，是國家生存與發展的根本前提。5年來的實踐證明，《香港國安法》是捍衛「一國兩制」、維護香港繁榮穩定的「守護神」，是具有重大歷史意義和現實意義的好法律。《香港國安法》及《維護國家安全條例》清楚訂明構成有關危害國家安全罪行的元素和刑罰，精準針對佔極少數從事危害國家安全的行為和活動的個人和組織，奉公守法的人不會誤墮法網，無需擔心。

"""
    sample_text = "This is a sample text with some words that are not on HSK1-2 level. For example, 'abandon', 'zealous', and 'quintessential'."
    generate_flashcards(trim)
    print("Flashcards generated and saved.")
    