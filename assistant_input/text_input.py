# text_input.py
from assistant_event_bus.event_bus import publish
import time

from assistant_tools.utils import play_sfx

def text_input_loop():
    while True:
        command = input("\nEnter your query into the V.E.G.A. system: \n")
        if command:
            publish("USER_SPEECH", query=command)
            play_sfx('select')  
            time.sleep(7)  # Задержка перед следующим вводом
        else:
            play_sfx('silent_error')
            print("No input detected. Please enter a valid query.")