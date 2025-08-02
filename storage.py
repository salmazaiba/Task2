
from threading import Lock

store = {}
store_lock = Lock()

def increment_click(code):
    with store_lock:
        store[code]["clicks"] += 1