import threading

isLocked = False
global_status = -1
global_text = []
split_byte_data = bytes(b"")

lock = threading.Lock()

model_id = ""
system = "You are an artificial assistant."
