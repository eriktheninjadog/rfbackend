#remotechineseclient.py


import requests
import json

# Define the URL to which you want to send the JSON request

def access_remote_client(endpoint,payload):
    base_url = 'https://chinese.eriktamm.com/api/'
    json_payload = json.dumps(payload)
    # Set the headers to indicate that the request is sending JSON data
    headers = {'Content-Type': 'application/json'}
    # Send the POST request with the JSON payload
    response = requests.post(base_url+endpoint, data=json_payload, headers=headers)

    # Check the response status code
    if response.status_code == 200:
        print('Request successful!')
        return response.json()['result']
    else:
        print('Request failed. Status code:', response.status_code + " " + endpoint)
        return None
        