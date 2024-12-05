#frequencytools.py
import dictionaryclient


class FrequencyCounter:
    def __init__(self):
        self.cached_dict = None
        self.dict_changes = 0
        self.dictionary_client = dictionaryclient.DictionaryClient()

    def _load_dict(self):
        if self.cached_dict is None:
            self.cached_dict = self.dictionary_client.get_values('frequency')

    def get_frequency(self, astr):
        self._load_dict()
        return int(self.cached_dict.get(astr, 0))
    
    def save_changes(self):
        self.dictionary_client.set_values('frequency', self.cached_dict)
        

    def add_frequency(self, astr):
        self._load_dict()
        if astr not in self.cached_dict:
            self.cached_dict[astr] = "1"
            ret = 1
        else:
            self.cached_dict[astr] = str(int(self.cached_dict[astr]) + 1)
            ret = int(self.cached_dict[astr])
        
        self.dict_changes += 1
        if self.dict_changes > 20:
            self.dict_changes = 0
            self.dictionary_client.set_values('frequency', self.cached_dict)
        return ret
