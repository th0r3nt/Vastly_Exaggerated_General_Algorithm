# text_input.py
from assistant_event_bus.event_bus import publish
import time

def text_input_loop():
    while True:
        command = input("\nEnter your query into the V.E.G.A. system: \n")
        if command:
            publish("USER_SPEECH", query=command)
            time.sleep(5)