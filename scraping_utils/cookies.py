import os, pickle

def load(path="cookies.pkl"):
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except:
            os.remove(path)
    return None

def save(cookies, path="cookies.pkl"):
    with open(path, "wb") as f:
        pickle.dump(cookies, f)
