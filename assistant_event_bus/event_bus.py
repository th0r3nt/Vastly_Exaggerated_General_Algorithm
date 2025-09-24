# event_bus.py
from assistant_tools.utils import play_sfx

class EventBus:
    def __init__(self):
        self.listeners = {}
        play_sfx("processing")
        print("\nEvent Bus: Initialized.\n")

    def subscribe(self, event_type: str, handler):
        """Подписывает компонент на какое либо событие"""
        if event_type not in self.listeners: 
            self.listeners[event_type] = []

        self.listeners[event_type].append(handler)

    def publish(self, event_type: str, *args, **kwargs): # Что делает publish? Он заглядывает в свой журнал self.listeners, находит там, к примеру, запись "USER_SPEECH", видит в списке подписчиков функцию generate_response и вызывает ее, передавая ей text=text.
        if event_type in self.listeners:
            for handler in self.listeners[event_type]: # "Пройдись по каждому подписчику эвента, и передай ему текст"
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    print(f"Event Bus: Error in handler '{handler.__name__}' for the event '{event_type}': {e}")

event_bus = EventBus()


# Функции обертки
def subscribe(event_type, handler):
    event_bus.subscribe(event_type, handler)

def publish(event_type, *args, **kwargs):
    event_bus.publish(event_type, *args, **kwargs)  