import pickle

class PersistentStack:
    def __init__(self, filename):
        self.filename = filename
        self.stack = []
        self.load()

    def load(self):
        try:
            with open(self.filename, 'rb') as f:
                self.stack = pickle.load(f)
        except FileNotFoundError:
            pass

    def save(self):
        with open(self.filename, 'wb') as f:
            pickle.dump(self.stack, f)

    def push(self, value):
        self.stack.append(value)
        self.save()

    def pop(self):
        if not self.stack:
            raise IndexError("pop from empty stack")
        value = self.stack[-1]
        del self.stack[-1]
        self.save()
        return value

    def peek(self):
        if not self.stack:
            raise IndexError("peek from empty stack")
        return self.stack[-1]
    
    def size(self):
        return len(self.stack)

    def __iter__(self):
        return iter(self.stack)

    def __repr__(self):
        return repr(self.stack)
    
