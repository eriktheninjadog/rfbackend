import time
import requests

import json
import openrouter

#free_sentence_translator_service.py
# Define the URL to which you want to send the JSON request
url = 'https://chinese.eriktamm.com/api/get_background_work'

urltrans = 'https://chinese.eriktamm.com/api/explain_sentence_free'

urladd = 'https://chinese.eriktamm.com/api/set_dictionary_value'



if __name__ == "__main__":
    for i in range(10000):    
        # Define the JSON payload for the request
        payload = {
            "processor":"sentencetranslator"
        }
        # Convert the payload to JSON format
        json_payload = json.dumps(payload)
        # Set the headers to indicate that the request is sending JSON data
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=json_payload, headers=headers)
        if response.status_code == 200:
            print('Request successful!')
            js = response.json()        
            workstring = js['result']         
            if workstring != None:
                print(workstring)
                try:
                    newpayload = {
                        "sentence": workstring
                    }
                    newpayload = json.dumps(newpayload)
                    response = requests.post(urltrans, data=newpayload, headers=headers)
                    js = response.json()
                    translation = js['result']
                    
                    if translation == None:
                        time.sleep(3600)
                    else:
                        newpayload = {
                            "key": workstring,
                            "value": translation,
                            "dictionary":"sentence_explanations"
                        }
                        newpayload = json.dumps(newpayload) 
                        response = requests.post(urladd, data=newpayload, headers=headers)
                        js = response.json()        
                        result = js['result']
                        time.sleep(120)
                except:
                    time.sleep(3600)                
            else:
                time.sleep(3600)
            
        else:
            print('Request failed. Status code:', response.status_code)
            






        
