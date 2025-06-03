import pickle

def save_macro(filename, events):
    with open(filename, 'wb') as f:
        pickle.dump(events, f)

def load_macro(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)
