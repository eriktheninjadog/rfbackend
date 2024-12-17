import json

dictionarypath  = "/var/www/html/scene/"

class PersistentDict:
    def __init__(self, filename):
        self.filename = dictionarypath + filename
        self.data = {}
        self.load()

    def load(self):
        try:
            with open(self.filename, 'r') as f:
                self.data = json.load(f)
        except IOError:
            pass

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f)
    
    def get_raw_data(self):
        return self.data

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.save()

    def __delitem__(self, key):
        del self.data[key]
        self.save()

    def __contains__(self, key):
        return key in self.data

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __repr__(self):
        return f'PersistentDict({self.filename!r}, {self.data!r})'