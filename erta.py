import json
from typing import List, Dict, Tuple, Iterator, Optional, Union, Callable


import json
import re

def split_string(input_string, split_char, max_length=4000):
    def find_last_split_index(s, start, end):
        for i in range(end, start - 1, -1):
            if s[i] == split_char:
                return i
        return -1  # If split_char is not found

    result = []
    start_index = 0

    while start_index < len(input_string):
        if start_index + max_length >= len(input_string):
            # If the remaining string is shorter than max_length, add it and break
            result.append(input_string[start_index:])
            break

        # Find the last occurrence of split_char within max_length
        end_index = find_last_split_index(input_string, start_index, start_index + max_length - 1)

        if end_index == -1:
            # If split_char is not found, force a split at max_length
            end_index = start_index + max_length
        else:
            # Include the split_char in the current part
            end_index += 1

        # Add the part to the result
        result.append(input_string[start_index:end_index])

        # Move the start_index for the next iteration
        start_index = end_index

    return result


class ERTATextProcessor:
    def __init__(self, file_path: str = None, text: str = None, splitter: Callable[[str], List[str]] = None):
        self.file_path = file_path
        self.data = {"content": [], "dictionary": {}}

        if file_path:
            self.read_file()
        elif text and splitter:
            self.populate_content_from_text(text, splitter)

    def read_file(self) -> None:
        """Read the ERTAText JSON file and load its content."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            print(f"ERTAText file not found: {self.file_path}")
        except json.JSONDecodeError:
            print(f"Invalid ERTAText JSON in file: {self.file_path}")

    def populate_content_from_text(self, text: str, splitter: Callable[[str], List[str]]) -> None:
        """Populate the content array using the provided text and splitter function."""
        self.data['content'] = []
        wordparts = split_string(text,'。')
        for part in wordparts:
            words = splitter(part)
            somecontent = [{"word": word} for word in words]
            self.data['content'].extend(somecontent)

    def populate_content_from_text_file(self, filename, splitter: Callable[[str], List[str]]) -> None:
        
        """Populate the content array using the provided text and splitter function."""
        
        self.data['content'] = []
        wordparts = split_string(text,'。')
        for part in wordparts:
            words = splitter(part)
            somecontent = [{"word": word} for word in words]
            self.data['content'].extend(somecontent)



    def write_file(self,newfilepath=None) -> None:
        """Write the current data to the ERTAText JSON file."""
        if self.file_path:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(self.data, file, ensure_ascii=False, indent=2)
        else:
            if newfilepath != None:
                with open(newfilepath, 'w', encoding='utf-8') as file:
                    json.dump(self.data, file, ensure_ascii=False, indent=2)            
            else:
                print("No file path specified. Cannot write to file.")

    def add_word_to_content(self, word: str, timepoint: Optional[float] = None) -> None:
        """Add a word to the ERTAText content list with an optional timepoint in seconds."""
        if timepoint is not None:
            self.data['content'].append({"word": word, "timepoint": timepoint})
        else:
            self.data['content'].append({"word": word})

    def add_word_to_dictionary(self, word: str, pronunciation: str, definition: str) -> None:
        """Add a word to the ERTAText dictionary with its pronunciation and definition."""
        self.data['dictionary'][word] = [pronunciation, definition]

    def get_word_info(self, word: str) -> Tuple[str, str]:
        """Get the pronunciation and definition of a word from the ERTAText dictionary."""
        if word in self.data['dictionary']:
            return tuple(self.data['dictionary'][word])
        return ("", "")

    def get_content(self) -> List[Dict[str, Union[str, float]]]:
        """Get the ERTAText content list."""
        return self.data['content']

    def get_dictionary(self) -> Dict[str, List[str]]:
        """Get the ERTAText dictionary."""
        return self.data['dictionary']
    
    def is_punctation(self,word):
        return word in [' ','\n','，','。']
            

    def get_undefined_words(self) -> List[str]:
        """
        Return a list of words from the content that are not in the dictionary.
        """
        undefined_words = []
        for item in self.data['content']:
            theword = item['word']
            if theword not in self.data['dictionary'] and not self.is_punctation(theword):
                undefined_words.append(theword)
        return list(set(undefined_words))  # Remove duplicates

    def enumerate_content(self) -> Iterator[Tuple[int, str, Optional[float]]]:
        """
        Return an enumerator for the content.
        Yields tuples of (index, word, timepoint) for each item in the content.
        """
        for index, item in enumerate(self.data['content']):
            yield (index, item['word'], item.get('timepoint'))

    def get_word_at_timepoint(self, target_timepoint: float) -> Optional[str]:
        """
        Return the word at or immediately before the given timepoint.
        Returns None if no word is found before the timepoint.
        """
        last_word = None
        for item in self.data['content']:
            if 'timepoint' in item:
                if item['timepoint'] > target_timepoint:
                    return last_word
                last_word = item['word']
        return last_word



import openrouter
def extract_json(string):
    # Find all substrings that look like JSON objects
    json_like_strings = re.findall(r'(\{.*?\}|\[.*?\])', string, re.DOTALL)
    
    # Try to parse each substring as JSON
    for json_string in json_like_strings:
        try:
            # If successful, return the parsed JSON
            return json_string
        except json.JSONDecodeError:
            # If parsing fails, continue to the next substring
            continue
    
    # If no valid JSON is found, return None
    return None


def beginner_chinese_splitter(str):
    jsonnewline = json.dumps('\n')
    jsonnewline = jsonnewline.replace('\'','')

    str = str.replace('\n','@')
    dirty  = openrouter.do_open_opus_questions("Split this text into useful words,idiomatic expressions and idioms suitable for a Cantonese lower intermediate learner. Include punctations. Also treat @ as a word and include this. Make the return in json like ['word1','word2','word3',...]. Only return json, no other text.\n"+ str)    
    dirty = dirty.replace('@','\\n')
    try:
        return json.loads(dirty)
    except:        
        return json.loads( extract_json(dirty) )


def chinese_ai_lookup(words):
    ask = json.dumps(words)
    return json.loads( openrouter.do_open_opus_questions("Take each one of the chinese words in the provided json structure and return json array looking like this ['words','jyutping','english definition']. Only return json, no other text .\n"+ ask) )



import requests

def call_api(base_url, endpoint, data):
    # Construct the full URL
    url = f"{base_url}/{endpoint}"
    # Set up the parameter
    try:
        # Make the GET request
        response = requests.post(url,json=data)
        
        # Check if the request was successful
        response.raise_for_status()        
        # Return the JSON response
        return response.json()
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

import constants

#    term = data.get(constants.PARAMETER_TERM)
#    jyutping = data.get(constants.PARAMETER_JYUTPING)
#    definition = data.get(constants.PARAMETER_DEFINITION)

def update_remote_directory(word,jyutping,english):
    data = {constants.PARAMETER_TERM:word, constants.PARAMETER_JYUTPING:jyutping,constants.PARAMETER_DEFINITION:english}    
    ret = call_api("https://chinese.eriktamm.com/api","update_dictionary",data)
    return ret

def remote_dictionary(word):
    data = {constants.PARAMETER_SEARCH_WORD:word }
    ret = call_api("https://chinese.eriktamm.com/api","dictionarylookup",data)
    return ret


# Example usage
if __name__ == "__main__":
    # Example splitter function
    
    thetext = """
    

2｜承諾改變





　　最近，我在治療一位年近三十的個案，在此稱他為喬。喬是個聰明伶俐的年輕人，也是冷面笑匠，而他來接受治療是希望建立自信並減輕焦慮。但治療過程對喬來說格外辛苦，因為他經歷過不少難熬、仍待他釐清意義的困境。有一回治療時，喬臉上帶著心照不宣的微微笑意，問我有沒有更簡單的辦法，能幫他順利解決生活難題。我一聽追問了幾句，而他的回答令我不禁莞爾，他說：「難道你就沒有其他辦法，能讓我啥事也不用做嗎──就像即食餐盒，現買現吃？」

　　我們倆一起笑了出來。你大概也料想得到，我只能告訴喬，可惜對於想要改變的人來說，這世上並沒有即食策略。改變可能很花時間，而喬為了創造他期望的重大改變，先要每天花時間努力，才能確實造成一點變化。

　　不過，喬倒是很快就開始運用我教他的技巧，去為生活創造有意義的積極改變。這一路走來並不容易，有時他必須離開舒適圈，但他已經改變信念，從原本自認只是「無名小卒」，到現在轉而肯定自己的價值，深信自己的聲音確實擁有影響力，最後更因此投身他的終生志向，努力進修成為記者。



有意識地作出承諾

　　「想要改變」和「真心承諾作出改變」是兩回事。這讓我想到，我曾在某個寒冷冬日裡，為倫敦某家大企業主持一場十分鐘入禪工作坊。我如常先來段輕鬆的開場白，接著邀請幾位願意分享的聽眾，大致談談他們的日常生活。現場有位名為瑪莉的聽眾，氣沖沖地談起她的生活。這番話想必大家再熟悉不過了：

　　「我覺得自己就像切換成自動駕駛般漂泊人生，感受不到真正的目的、熱情或方向，而且經常覺得不堪負荷、無法清晰思考或作出決定。我的心也與我作對似的，只會往最壞處想，還不時對我妄加批判、否定及審判。此外我也覺得壓力很大，大部分時候都覺得身心俱疲。」

　　瑪莉很幸運，透過這套十分鐘入禪休息法，她終於能洞見自己的幸福，是怎麼被過去消極的思考模式所摧毀。一旦明白這點，她就能改變舊有的生活方式、從容處理生活所需。藉由每天撥出時間和空間來實踐十分鐘入禪休息法，瑪莉終於領會新的思考模式與感受方式，並迎來人生的巨大轉變。

　　如果瑪莉的話能引起你一絲共鳴，那麼也該是你振作並考慮改變的時刻了。活得身心俱疲並不代表活得完整，不過是狼狽維生罷了。因此，我請你現在停下來，花一分鐘就好，請你想一想：



花點時間……

　　你是真心想改變，想活得更充實而平靜，不再只是狼狽維生嗎？

　　請將省思過程中出現的想法或任何感受，簡短記錄在下邊空白處，或寫在筆記本上。







　　如果你對我剛才的問題回答「是」，那很好，這可能是你的一大進步。（如果你回答「不是」，還是請你繼續讀下去吧。或許我能改變你的心意！）在我們繼續討論十分鐘入禪休息法之前，我想先稍微談談「改變」。



擁抱改變

　　真正的改變需要時間，也需要你全心投入。或許你在一開始會感到氣餒，改變過程可能也不好受，但它會推著我們走出舒適圈。我們受到生性憂懼的一面影響，傾向拒絕改變，只想躲回安樂窩，但在十分鐘入禪休息法中，我會不斷鼓勵你張開雙手，擁抱改變。先要冒險改變，才能為你的生命迎來無數嶄新的可能。而且，你並不是孤軍奮戰，就像其他正在閱讀本書的夥伴一樣，你也在努力理解一些看似很沒意義的事情。又或許，只要想到自己是志趣相投的十分鐘入禪社群的一分子，社群成員都不願只是隨波逐流苟且生存，而是朝著充實而完整的生活邁進，便能感到寬慰。

　　一切改變都從你開始，此外還有一些約定需要請你遵守。



花點時間……

　　現在請你思考另一個問題：

　　你願意展開十分鐘入禪之旅，每一天都全心投入這十分鐘嗎？



為什麼稱之為「鍛鍊」？

　　接下來要從我的立場出發，跟你談談條件。如果你認同我的觀點，那麼，光是主動加入並積極「鍛鍊」十分鐘入禪休息法，就是你變得更好的開始。我之所以特意稱其為「鍛鍊」，是因為十分鐘入禪休息法正是可以改善心智活動，進而提升生活品質的心理鍛鍊。而且，這套方法運作的原理就像鍛鍊身體──如果你不規律上健身房（或許也該調整飲食習慣），身體就不會出現任何變化。

　　而大腦也一樣，我們要訓練心智、強化心智，並培養心智的靈活度──就如同訓練身體。不過要記得，你得規律鍛鍊才行。也就是說，你不能光是知道該怎麼做，還必須付諸實踐。因此，我要和你約法三章，一旦你作好準備，就必須主動參與。這意味著，你不但要全力以赴，還要把這十分鐘擺第一順位，視為每天不可或缺的一環。畢竟，我的指導和本書內容只是約定的一部分，其餘部分就操之在你了。

　　所以現在問題是，我們達成協議了嗎？



立下承諾，重建清晰思維

　　如果沒有異議，我要請你做件很簡單的事：



花點時間……

　　現在請你停下來一分鐘，閉上雙眼、做幾次呼吸。接著，請你創作一則專屬於你的短句，作為「你會嘗試鍛鍊，且每天會騰出十分鐘來照顧心理健康」的契約性承諾。

　　分享一下我寫的句子，或許有幫助：

　　「我承諾每天都會為了自己而鍛鍊，並懷著仁慈善意照看內心。」

　　請將你與自己立下的約定寫在左方空白處，或寫在一張卡片上。你可能想用手機把它拍成照片，以便終日提醒自己這項承諾：







如何駕馭內心小劇場

　　聽聽曾經受益於這項簡單承諾者的說法，或許對你有幫助。彼得是我私人執業之客戶，當他因公得搭飛機出差時，總是倍感壓力。不久前，他談到自己搭機時遇上亂流，而變得極度焦慮：「結果一路上，我的心告訴我一堆可能的意外事故，或有人會劫機，或飛行員忘了開啟安全帶燈號……我的心臟怦怦狂跳，渾身冒汗，一心只想趕快下飛機。」

　　想也知道，他的內心小劇場完全沒有現實根據。後來，彼得將十分鐘入禪休息法學以致用，退一步觀察這種憂慮，才發現自己的心智已經陷入災難化思考（catastrophizing，即一下子就往最壞處想）。於是每當彼得感到焦慮時，他就會進行敲打與呼吸練習（我們會在第五章、第六章詳述這兩種技巧），好讓自己立刻放鬆下來。如今，彼得甚至能享受飛行，因為他知道每當自己感到恐懼或焦慮時，就能運用這些技巧。他也學會降低心中窮緊張雜音的音量，並重拾更加理智且有益的思考方式。

　　開始鍛鍊十分鐘入禪休息法後，就能提升自身的安全感與掌控感，進而駕馭令你焦慮或棘手的情況。如果你在某些情況下曾感到焦躁不安（我們大多數人都會這樣），那麼撥出一點時間按照本書指示鍛鍊，對你可能大有幫助。或許有些時候，你連自己為什麼緊張都不清楚，只知道憂慮的感覺確實存在。這是因為我們的心智基本上是以「威脅模式」（threat mode）運作，但時時處在那種模式未必有幫助。因此，我們的目標就是讓威脅模式只在必要時刻運作。在切斷威脅模式後，你會瞬間感到平靜而放鬆，因而能夠更清晰思考。（我在下一章會更詳細說明這一點。）



苦惱的震央

　　我覺得有趣的是，我們滿腦子都是自己看起來如何、穿什麼衣服、做什麼工作、賺多少錢等等，卻不太在意自己的心。偏偏在我們感到苦惱時，心往往是撼動我們的震央。讓我們面對現實吧：有時候，我們的心就像一群狂躁的高空鞦韆藝人，從一個煩惱飛速盪向另一個煩惱，快得連奧運選手也要自嘆弗如。

　　我自己也曾數度遭逢人生重大失落，如痛失親友、關係觸礁，或純粹是在嚴酷的生活考驗中苦苦掙扎，而經歷了異常艱難的低潮期（通常還會伴隨著各種難受的情緒）。而且我發現，我的大腦似乎會特別增強某些情緒──我腦中的「威脅偵測中心」（又稱為杏仁核）似乎會過度活化。我努力要處理所有情緒，偏偏杏仁核在賣力幫倒忙。而我要說的重點是，不論你在生活中遭遇什麼情況，未必總能指望大腦擔任最佳戰友。

　　每個正在讀這本書的人，都會有則屬於自己的故事──關於失落、拒絕、拋棄，以及其他任何生命考驗的故事。然而，這些就只是關於你人生的故事，它們無法定義你是誰。唯有你選擇的回應方式，才能決定「你是誰」。

　　我們都聽過人家說：「我的心在愚弄我自己。」其實，你的心做了一大堆你目前渾然不覺的事，像是刪除、加劇或災難化令人為難的真相。這可能發生在日常生活的各種情況中：

老闆看你的表情很古怪，但這不表示你會被開除。
昨天伴侶忘了回你訊息，但他還是像以前一樣愛你。
你才剛遭遇失敗，卻不表示你一點用也沒有。
吃早餐時，正值青春期的女兒說她「恨」你，意思大概是「只恨你一下下」，而不是向來或永遠都恨你──差不多再過半小時，她就會跑來說愛你了。
今天，你在星巴克不過是點杯卡布奇諾，但店員看你的表情，就好像你剛才要他移植腎臟給你。他八成只是那天心情不好，並不是真的討厭你。
　　有時大腦需要一點「停機時間」（就像身體在日間也需要休息），才能幫助我們重拾洞察力。而我們同樣要了解，自己為什麼會有那種反應，才能順利轉換思考角度。

　　本書就是要協助你改變觀點，讓你活得更恬適、更平靜，最終變得更有適應力。既然十分鐘入禪休息法好處多多，每天十分鐘根本不算什麼，想必你也有同感吧！



花點時間……

　　我要問你另一個問題：

　　你多常花時間留意並維護自己的心理健康呢？

　　現在請暫停一下，想一想剛才的問題。

　　你的答案是什麼？



　　我猜，你們多數人的答案是「從來沒有」、「幾乎沒有」或「不太頻繁」，理由則是「我沒空」。如果真被我猜中，則歡迎、歡迎、歡迎你！等你開始全心投入真正的改變，親身感受實踐的好處後，答案大概會變得很不一樣。

　　如果不好好照顧大腦，它就會像脫韁野馬般失去控制，造成許多有害的後果──這是無法迴避的事實。我從自己的專業知識、經驗和情感中發現，我們都必須設法多了解自己的心，並妥善照顧它。同時，我們也必須重新理解自己，用更仁慈和悲憫的態度來對待自己。只要呵護內心、體恤自己，就能大幅改變一切。

　　所以，安全帶繫好囉，請你放輕鬆享受這份生而為人所必經受的美麗混亂，跟著我一起展開旅程吧！每天只要十分鐘，就能找回寧靜的心，而你已經在改變的路上。
    
"""
    
    
    extract_json('json\n{"hihere":"jones"}')
    pop = ERTATextProcessor(text=thetext,splitter=beginner_chinese_splitter)

    pop.write_file("test2.json")


    for i in pop.get_undefined_words():
        result = remote_dictionary(i) 
        if result != None:
            if result['result'] != None:
                pop.add_word_to_dictionary(i,result['result'][1],result['result'][2])   


    for i in pop.get_undefined_words():
        print(i)
        
    ret = chinese_ai_lookup(pop.get_undefined_words())
            
    for i in ret: 
        word = i[0]
        jyutping = i[1]
        english = i[2]
        update_remote_directory(word,jyutping,english)
        pop.add_word_to_dictionary(word,jyutping,english)
        print(str(i))
        
        
    pop.write_file("test.json")

    None
    """
    
    def simple_splitter(text: str) -> List[str]:
        return text.split()

    # Create an ERTATextProcessor instance with a text string and splitter function
    text = "This is a sample text for testing the new constructor."
    processor = ERTATextProcessor(text=text, splitter=simple_splitter)

    # Print the content to verify it's been populated
    print("ERTAText Content:", processor.get_content())

    # Add some words to the dictionary
    processor.add_word_to_dictionary("sample", "sam-puh l", "a small part or quantity intended to show what the whole is like")
    processor.add_word_to_dictionary("testing", "tes-ting", "the process of evaluating a system or its component(s) with the intent to find whether it satisfies the specified requirements or not")

    # Print the dictionary
    print("ERTAText Dictionary:", processor.get_dictionary())

    # Get undefined words
    undefined_words = processor.get_undefined_words()
    print("Undefined words in ERTAText content:", undefined_words)

    # Enumerate content
    print("Enumerated content:")
    for index, word, timepoint in processor.enumerate_content():
        print(f"  {index}: {word} (Timepoint: {timepoint} seconds)")

    # Try to write to a file (this will print a message since no file path was specified)
    processor.write_file()
    """