# text_input.py
from assistant_event_bus.event_bus import publish
from assistant_event_bus import event_definitions as events
from assistant_tools.utils import play_sfx
import time
import logging
from assistant_general.logger_config import setup_logger

setup_logger()
logger = logging.getLogger(__name__)

def text_input_loop():
    while True:
        command = input("\nEnter your query into the V.E.G.A. system: \n")
        if command:
            publish(events.USER_SPEECH, query=command)
            play_sfx('select')  
            time.sleep(10)  # Костыль-задержка перед следующим вводом
        else:
            play_sfx('silent_error')
            logger.error("No input detected. Please enter a valid query.")