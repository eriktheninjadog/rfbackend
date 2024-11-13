import time
import requests

import json

#free_sentence_translator_service.py
# Define the URL to which you want to send the JSON request
url = 'https://chinese.eriktamm.com/api/get_background_work'


if __name__ == "__main__":
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
                        
        else:
            time.sleep(3600)
        
    else:
           print('Request failed. Status code:', response.status_code)
        






        
