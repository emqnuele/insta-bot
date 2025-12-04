import random
import time

def calculate_delay(text):
    delay = min(5.0, max(1.0, len(text) * 0.05 + random.uniform(0.5, 1.5)))
    return delay

test_messages = [
    "ciao",
    "come stai?",
    "questo è un messaggio un po' più lungo per vedere quanto tempo ci mette",
    "ok"
]

print("Testing delay calculation:")
for msg in test_messages:
    delay = calculate_delay(msg)
    print(f"Message: '{msg}' (len {len(msg)}) -> Delay: {delay:.2f}s")
