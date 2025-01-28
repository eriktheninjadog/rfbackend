import requests
import json
import random
import wordlists
import textprocessing
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional, Union
from pathlib import Path

class OpenRouterAPI:
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    def __init__(self, domain: str = "chinese.eriktamm.com", app_name: str = "chinese_app"):
        self.bearer_key = self._read_bearer_key()
        self.headers = {
            "Authorization": self.bearer_key,
            "HTTP-Referer": domain,
            "X-Title": app_name
        }
        self._setup_logging()

    def _setup_logging(self):
        log_dir = Path('/var/log/openrouter')
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a logger
        self.logger = logging.getLogger('openrouter')
        self.logger.setLevel(logging.INFO)
        
        # Create handlers
        current_date = datetime.now().strftime('%Y-%m-%d')
        file_handler = logging.FileHandler(
            log_dir / f'openrouter_{current_date}.log',
            encoding='utf-8'
        )
        
        # Create formatters and add it to handlers
        log_format = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(log_format)
        
        # Add handlers to the logger
        self.logger.addHandler(file_handler)

    def _log_request_response(self, model: str, messages: List[Dict], response: Dict):
        # Mask the bearer token in headers
        safe_headers = self.headers.copy()
        if 'Authorization' in safe_headers:
            safe_headers['Authorization'] = '[MASKED]'

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'request': {
                'headers': safe_headers,
                'messages': messages
            },
            'response': response
        }
        
        self.logger.info(json.dumps(log_entry, ensure_ascii=False, indent=2))

    def _read_bearer_key(self) -> str:
        try:
            with open('/var/www/html/api/rfbackend/routerkey.txt', 'r') as f:
                return f.readline().strip()
        except FileNotFoundError:
            raise Exception("API key file not found")

    def do_opus_questions(self):
        question = self.create_poe_example_question('A1', 20)
        response = self._make_request("anthropic/claude-3-opus", [{"role": "user", "content": question}])
        with open('opusanswer.json', 'w', encoding='utf-8') as f:
            json.dump(response, f)
        self.parse_router_json(response)

    def do_open_opus_questions(self, question: str) -> str:
        return self.get_completion("anthropic/claude-3.5-sonnet", question)

    def open_router_nemotron_70b(self, user_content: str) -> str:
        return self.get_completion(
            "nvidia/llama-3.1-nemotron-70b-instruct",
            user_content,
            "You are an assistant used to summarize and simplify news"
        )

    def open_router_qwen_25_72b(self, user_content: str) -> str:
        return self.get_completion(
            "qwen/qwen-2.5-72b-instruct",
            user_content,
            "You are an assistant"
        )        
    
    def open_router_meta_llama_3_1_8b(self, user_content: str) -> str:
        return self.get_completion(
            "meta-llama/llama-3.1-8b-instruct",
            user_content
        )

    def open_router_chatgpt_4o1_preview(self, system_content: str, user_content: str) -> str:
        return self.get_completion(
            "openai/o1-preview",
            user_content,
            system_content
        )

    def open_router_chatgpt_4o(self, system_content: str, user_content: str) -> str:
        return self.get_completion(
            "openai/chatgpt-4o-latest",
            user_content,
            system_content
        )

    def open_router_chatgpt_4o_mini(self, system_content: str, user_content: str) -> str:
        return self.get_completion(
            "openai/gpt-4o-mini",
            user_content,
            system_content
        )

    def open_router_claude_3_5_sonnet(self, system_content: str,text: str) -> str:
        return self.get_completion(
            "anthropic/claude-3.5-sonnet",
            text,
            system_content=system_content
        )
        

    def open_router_meta_llama_3_2_3b_free(self, text: str) -> str:
        return self.get_completion(
            "meta-llama/llama-3.2-3b-instruct:free",
            text
        )
        
    def open_router_meta_llama_3_2_3b(self, text: str) -> str:
        return self.get_completion(
            "meta-llama/llama-3.2-3b-instruct",
            text
        )
        
    def open_router_mistral_7b_instruct(self, text: str) -> str:
        return self.get_completion(
            "mistralai/mistral-7b-instruct-v0.3",
            text
        )


    def open_router_nova_micro_v1(self, user_content: str) -> str:
        return self.get_completion(
            "amazon/nova-micro-v1",
            user_content)

    def open_router_deepseek_r1(self, user_content: str) -> str:
        return self.get_completion(
            "deepseek/deepseek-r1",
            user_content)

    def open_router_deepseek_r1(self, user_content: str) -> str:
        return self.get_completion(
            "deepseek/deepseek-r1",
            user_content)


    def open_router_qwen(self, system_content: str, user_content: str) -> str:
        return self.get_completion(
            "qwen/qwen-2.5-72b-instruct",
            user_content,
            system_content
        )

    def _make_request(self, model: str, messages: List[Dict[str, str]]) -> Dict:
        try:
            request_data = {
                "model": model,
                "messages": messages
            }
            
            self.logger.info(f"Making request to {model}")
            self.logger.debug(f"Request data: {json.dumps(request_data, ensure_ascii=False)}")
            
            response = requests.post(
                url=self.BASE_URL,
                headers=self.headers,
                data=json.dumps(request_data)
            )
            response.raise_for_status()
            response_json = response.json()
            
            # Log the request and response
            self._log_request_response(model, messages, response_json)
            
            return response_json
        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def get_completion(self, model: str, user_content: str, system_content: Optional[str] = None) -> str:
        messages = [{"role": "user", "content": user_content}]
        try:
            if system_content:
                messages.append({"role": "system", "content": system_content})
            
            self.logger.info(f"Getting completion from {model}")
            response = self._make_request(model, messages)
            print(str(response))
            return response['choices'][0]['message']['content']
        except Exception as e:
            error_msg = f"Error getting completion: {str(e)}"
            self.logger.error(error_msg)
            print("error: " + error_msg)
            return "AI Error"
        
    def parse_router_json(self, response_dict: Dict) -> None:
        try:
            choices = response_dict['choices']
            message = choices[0]['message']
            examples = message['content']
            parsed_examples = json.loads(examples)
            result = self.new_parse_poe(parsed_examples)
            cache = ExampleCache()
            cache.add_examples(result)
            self.logger.info("Successfully parsed and cached router JSON response")
        except Exception as e:
            error_msg = f"Error parsing router JSON: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)

    @staticmethod
    def new_parse_poe(result_list: List[Dict]) -> List[Dict]:
        return [
            {
                "chinese": textprocessing.split_text(item['chinese']),
                "english": item['english']
            }
            for item in result_list
        ]

class ExampleCache:
    def __init__(self, cache_path: str = '/var/www/html/scene/examplescache.txt'):
        self.cache_path = Path(cache_path)
        self.logger = logging.getLogger('openrouter.cache')

    def read(self) -> List:
        try:
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                data = json.loads(f.read())
                self.logger.info(f"Successfully read cache from {self.cache_path}")
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.warning(f"Cache read error: {str(e)}")
            return []

    def save(self, cache: List) -> None:
        try:
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False)
            self.logger.info(f"Successfully saved cache to {self.cache_path}")
        except Exception as e:
            self.logger.error(f"Cache save error: {str(e)}")
            raise

    def add_examples(self, examples: List) -> None:
        try:
            cache = self.read()
            cache.append(examples)
            self.save(cache)
            self.logger.info(f"Added {len(examples)} new examples to cache")
        except Exception as e:
            self.logger.error(f"Error adding examples to cache: {str(e)}")
            raise

    def pick_random_sentence(self) -> Optional[Dict]:
        repos = self.read()
        if not repos:
            self.logger.warning("No sentences available in cache")
            return None
        repo = random.choice(repos)
        selected = random.choice(repo)
        self.logger.debug(f"Selected random sentence: {selected}")
        return selected

    def pick_random_sentences(self, count: int) -> List[Dict]:
        sentences = [s for s in (self.pick_random_sentence() for _ in range(count)) if s is not None]
        self.logger.info(f"Selected {len(sentences)} random sentences")
        return sentences

class CantoneseQuestionGenerator:
    def __init__(self, cache: ExampleCache):
        self.cache = cache
        self.logger = logging.getLogger('openrouter.generator')

    def create_proper_cantonese_questions(self, level: str, number_of_sentences: int) -> str:
        self.logger.info(f"Creating {number_of_sentences} proper Cantonese questions at level {level}")
        sentences = self.cache.pick_random_sentences(number_of_sentences)
        sentence_list = '\n'.join(''.join(s['chinese']) for s in sentences)
        return ("""For each sentence in the list, rewrite it into plain spoken Cantonese. 
                 Return these together with english translation in json format like this: 
                 [{\"english\":ENGLISH_SENTENCE,\"chinese\":CANTONESE_TRANSLATION}]. 
                 Only respond with the json structure. Here is the list: \n""" + sentence_list)

    def create_pattern_example_question(self, level: str, number_of_sentences: int) -> str:
        self.logger.info(f"Creating {number_of_sentences} pattern example questions at level {level}")
        return f"""Create {number_of_sentences} examples in Cantonese using the following 
                sentence pattern: {wordlists.pick_sample_sentence__pattern()}. 
                Return these together with english translation in json format like this: 
                [{"english":ENGLISH_SENTENCE,"chinese":CANTONESE_TRANSLATION}]. 
                Only respond with the json structure.")"""

    def create_poe_example_question(self, level: str, number_of_sentences: int) -> str:
        self.logger.info(f"Creating {number_of_sentences} POE example questions at level {level}")
        if random.random() > 0.3:
            return self.create_pattern_example_question(level, number_of_sentences)
        
        return (f"""Create {number_of_sentences} sentences at A1 level including some the 
                following words: {wordlists.get_sample_A1_wordlist(30)}. 
                Return these together with vernacular cantonese translation 
                (use traditional charactters) in json format like this: 
                [{"english":ENGLISH_SENTENCE,"chinese":CANTONESE_TRANSLATION}]. 
                Only respond with the json structure.")""")

if __name__ == "__main__":
    # Set up root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    api = OpenRouterAPI()
    response = api.open_router_chatgpt_4o(
        "You are a Cantonese language expert, specializing in correcting errors in transcriptions based upon context.",
        "Here is a transcription. Each word is on a new line. Give the lines where you think there are mistakes and what the proper word should be:"
    )
    print(response)