# event_bus.py
from assistant_tools.utils import play_sfx
from assistant_general.logger_config import setup_logger
import logging

setup_logger()
logger = logging.getLogger(__name__)

# Сюда в будущем можно добавить отдельную шину для графического интерфейса

class EventBus: # Класс был создан для того, чтобы хранить переменную listeners без global (Также для инкапсуляции: класс прячет listeners от других функций)
    def __init__(self):
        play_sfx("processing")
        self.listeners = {}
        logging.info("\nEvent Bus: Initialized.\n")

    def subscribe(self, event_type: str, handler):
        """Подписывает компонент на какое либо событие"""
        if event_type not in self.listeners: 
            self.listeners[event_type] = []

        logger.debug(f"Handler '{handler.__name__}' subscribed to event '{event_type}'.")
        self.listeners[event_type].append(handler)

    def publish(self, event_type: str, *args, **kwargs): # Что делает publish? Он заглядывает в свой журнал self.listeners, находит там, к примеру, запись "USER_SPEECH", видит в списке подписчиков функцию generate_response и вызывает ее, передавая ей text=text.
        logger.info(f"Publishing event: '{event_type}' with data: {kwargs}")
        if event_type in self.listeners:
            for handler in self.listeners[event_type]: # "Пройдись по каждому подписчику эвента, и передай ему текст (либо другие данные)"
                try:
                    logger.debug(f"  -> Triggering handler '{handler.__name__}' for event '{event_type}'.")
                    handler(*args, **kwargs)
                except Exception as e:
                    play_sfx("error")
                    logger.error(f"Event Bus: Error in handler '{handler.__name__}' for event '{event_type}': {e}", exc_info=True)
        else:
            logger.info(f"Event '{event_type}' was published, but has no listeners.")


event_bus = EventBus()

# Функции обертки
def subscribe(event_type, handler):
    play_sfx('silent_execution')
    event_bus.subscribe(event_type, handler)

def publish(event_type, *args, **kwargs):
    play_sfx('silent_execution')
    event_bus.publish(event_type, *args, **kwargs)  