#make examples

import requests
import json

# Define the URL to which you want to send the JSON request
url = 'https://chinese.eriktamm.com/api/poeexamples'

# Define the JSON payload for the request
payload = {
    "onlyFailed":False,
    "number":20,
    "level":"A1",
    "language":"hi",
    "store":True
}

# Convert the payload to JSON format
json_payload = json.dumps(payload)

# Set the headers to indicate that the request is sending JSON data
headers = {'Content-Type': 'application/json'}

# Send the POST request with the JSON payload
for i in range(10):
    response = requests.post(url, data=json_payload, headers=headers)

    # Check the response status code
    if response.status_code == 200:
        print('Request successful!')
        print('Response:', response.json())
    else:
        print('Request failed. Status code:', response.status_code)