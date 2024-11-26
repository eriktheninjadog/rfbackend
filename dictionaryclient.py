import requests

class DictionaryClient:
    def __init__(self):
        self.base_url = "https://chinese.eriktamm.com/api"

    def set_dictionary_value(self, dictname, keyvalue, value):
        url = f"{self.base_url}/set_dictionary_value"
        data = {
            'dictionary': dictname,
            'key': keyvalue,
            'value': value
        }
        response = requests.post(url, json=data)
        return response.json()

    def get_dictionary_value(self, dictname, keyvalue):
        url = f"{self.base_url}/get_dictionary_value"
        data = {
            'dictionary': dictname,
            'key': keyvalue
        }
        response = requests.post(url, json=data)
        return response.json()

    def get_values(self,dictname):
        url = f"{self.base_url}/download_dictionary"
        data = {
            'dictionary': dictname
        }
        response = requests.post(url, json=data)
        return response.json()['result']

    def set_values(self,dictname,new_dict):
        url = f"{self.base_url}/upload_dictionary"
        data = {
            'dictionary': dictname,
            'values':new_dict
        }
        response = requests.post(url, json=data)
        return response.json()
