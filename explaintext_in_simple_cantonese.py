#explaintext_in_simple_cantonese.py
import openrouter
import mp3helper
import pydub

def explain_text(txt):
    sentences = txt.split('。')
    totalText = txt
    api = openrouter.OpenRouterAPI()
    print("eplain text ")
    totalText += " full text for a 7 year old   "
    explain = api.open_router_claude_3_5_sonnet("You are a cantonese speaker helping foreigners learning Cantonese. Only respond using Cantonese written with Traditional Chinese","Explain the content of this text in simple spoken cantonese that a 8 year old can understand:" + txt)
    totalText += '\n' + explain
    totalText += " full text for a 10 year old   "
    explain = api.open_router_claude_3_5_sonnet("You are a cantonese speaker helping foreigners learning Cantonese. Only respond using Cantonese written with Traditional Chinese","Explain the content of this text in simple spoken cantonese that a 11 year old can understand:" + txt)
    totalText += '\n' + explain
    #totalText += " full text for a 10 year old   "  
#    explain = api.open_router_chatgpt_4o("You are a cantonese speaker helping foreigners learning Cantonese. Only respond using Cantonese written with Traditional Chinese","Explain the content of this text in simple spoken cantonese that a 10 year old can understand:" + txt)
#    totalText += '\n' + explain

    for sentence in sentences:
        if len(sentence) > 0:
            totalText += " original sentence   "
            totalText += sentence

            totalText += " 5 year old   "
            explain = api.open_router_claude_3_5_sonnet("You are a cantonese speaker helping foreigners learning Cantonese. Only respond using Cantonese written with Traditional Chinese","Explain the content of this sentence in simple spoken cantonese that a 8 year old can understand:" + sentence)
            totalText += '\n' + explain
            totalText += " 8 year old   "
            explain = api.open_router_claude_3_5_sonnet("You are a cantonese speaker helping foreigners learning Cantonese. Only respond using Cantonese written with Traditional Chinese","Explain the content of this sentence in simple spoken cantonese that a 11 year old can understand:" + sentence)
            totalText += '\n' + explain
 #           totalText += " 10 year old   "
  #          explain = api.open_router_chatgpt_4o("You are a cantonese speaker helping foreigners learning Cantonese. Only respond using Cantonese written with Traditional Chinese","Explain the content of this sentence in simple spoken cantonese that a 10 year old can understand:" + sentence)
   #         totalText += '\n' + explain

        if len(sentence) > 0:
            totalText += " original sentence  concepts "
            explain = api.open_router_claude_3_5_sonnet("You are a cantonese speaker helping foreigners learning Cantonese. Only respond using Cantonese written with Traditional Chinese","Explain the important terms in sentence in simple spoken cantonese that a 5 year old can understand:" + sentence)
            totalText += " 5 year old   "
            totalText += '\n' + explain
            explain = api.open_router_claude_3_5_sonnet("You are a cantonese speaker helping foreigners learning Cantonese. Only respond using Cantonese written with Traditional Chinese","Explain the important terms in sentence in simple spoken cantonese that a 8 year old can understand:" + sentence)
            totalText += " 8 year old   "
            totalText += '\n' + explain   
     #       explain = api.open_router_chatgpt_4o("You are a cantonese speaker helping foreigners learning Cantonese. Only respond using Cantonese written with Traditional Chinese","Explain the important terms in the sentence in simple spoken cantonese that a 10 year old can understand:" + sentence)
      #      totalText += " 10 year old   "
       #     totalText += '\n' + explain   
    return totalText
    



def split_text(text, max_length=3000):
    """Split text into chunks not exceeding max_length."""
    # Split at word boundaries (spaces)
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + max_length, len(text))
        # Ensure we don't split words in half
        if end < len(text) and text[end] != ' ':
            # Find the last space or newline character
            space_pos = text.rfind(' ', start, end)
            newline_pos = text.rfind('\n', start, end)
            space_pos = text.rfind(' ', start, end)
           
            # Use the rightmost position of either space or newline
            split_pos = max(space_pos, newline_pos)
            end = split_pos + 1 if split_pos >= 0 else end
        chunks.append(text[start:end].strip())
        start = end

    return chunks

import os
import os.path
def text_to_combined_mp3(text, output_filename, cantonese_text_to_mp3):
    """Convert text to one combined MP3 file using the specified text-to-MP3 function."""
    # Split text into manageable chunks
    text_chunks = split_text(text)
    temp_files = []

    try:
        # Convert each text chunk to a temporary MP3 file
        for i, chunk in enumerate(text_chunks):
            temp_filename = f'temp_chunk_{i}.mp3'
            cantonese_text_to_mp3(chunk, temp_filename)
            temp_files.append(temp_filename)

        # Combine all temporary MP3 files into one
        combined = pydub.AudioSegment.empty()

        for temp_file in temp_files:
            audio_segment = pydub.AudioSegment.from_file(temp_file)
            combined += audio_segment

        # Export the final combined audio
        combined.export(output_filename, format='mp3')

    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

import random
import subprocess
def explain_and_render_text(text,filename=None):
    if filename == None:
        filename = "spokenarticle_news_exp"+ str(random.randint(100,999))+".mp3"
    fulltext = explain_text(text)
    #split the text into 
    text_to_combined_mp3(fulltext, filename, mp3helper.cantonese_text_to_mp3)
    scp_command = f"scp {filename} chinese.eriktamm.com:/var/www/html/mp3"
    print(scp_command)
    result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)


import textprocessing
import json
def just_render_text(text,filename=None):
    if filename == None:
        filename = "spokenarticle_news_exp"+ str(random.randint(100,999))+".mp3"
    fulltext = text
    #split the text into 
    arr = textprocessing.split_text(fulltext)
    f = open(filename+".hint.json", "w",encoding="utf-8")
    f.write(json.dumps(arr))
    f.close()
    text_to_combined_mp3(fulltext, filename, mp3helper.cantonese_text_to_mp3)
    scp_command = f"scp {filename}* chinese.eriktamm.com:/var/www/html/mp3"
    print(scp_command)
    result = subprocess.run(scp_command, shell=True, capture_output=True, text=True)




if __name__ == "__main__":
    explain_and_render_text("""北韓傳媒報道，俄羅斯總統普京向領袖金正恩發出新年賀信，強調在新的一年俄朝將繼續加強合作，更加一致應對威脅和挑戰。

普京在信中向金正恩表示，今年6月他與金正恩在平壤舉行會晤，將俄朝關係提升至新的高度。會談後簽訂的《俄朝全面戰略夥伴關係條約》為從根本上擴大俄朝所有主要領域的互利雙邊合作提供條件。相信在2025年，俄朝將緊密地履行這一歷史性條約，更加一致地應對當前威脅和挑戰。這也符合兩國和兩國人民的根本利益。

韓聯社報道，北韓今年為普京的新年賀信單獨開篇，沒有像往年，與中國國家主席習近平等其他國家元首發來的新年一起報道，意在彰顯朝俄緊密合作。""")


#10.673