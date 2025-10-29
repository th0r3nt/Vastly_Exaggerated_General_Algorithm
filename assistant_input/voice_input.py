# voice_input.py
import threading
import vosk
import json
import sounddevice
import queue
from assistant_event_bus import event_definitions as events
from assistant_tools.utils import play_sfx
import os
from dotenv import load_dotenv
import logging
from assistant_general.logger_config import setup_logger

setup_logger()
logger = logging.getLogger(__name__)

load_dotenv() # для загрузки API ключей и путей из .env
VOSK_LOCAL_MODEL_PATH = os.getenv("VOSK_LOCAL_MODEL_PATH")

print("\n")

class SpeechListener(threading.Thread):
    """Слушает речь пользователя и кладет в очередь"""
    def __init__(self):
        super().__init__()
        self.audio_queue = queue.Queue()
        self.daemon = True

        try: # Инициализация Vosk
            model_path = VOSK_LOCAL_MODEL_PATH # Либо vosk-model-ru-0.42 (тяжелая версия), либо vosk-model-small-ru-0.22
            self.model = vosk.Model(model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
            print("\nThe local speech recognition engine (Vosk) has been initialized successfully.")
        except Exception as e:
            logger.error(f"Error: Failed to initialize Vosk: {e}")
            play_sfx("error")
            self.recognizer = None

    def _audio_callback(self, indata, frames, time, status):
        """Единственная задача - складывать аудиоданные в очередь"""
        self.audio_queue.put(bytes(indata))

    def run(self):
        """Основной цикл потока-слушателя"""
        if not self.recognizer: # Если Vosk не инициализировался, поток завершает работу
            play_sfx("silent_error")
            logger.error("Vosk was not initialized.")
            return
        
        else:
            from assistant_event_bus.event_bus import publish
            print("Listening Stream (Vosk): started.\n")
            with sounddevice.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=self._audio_callback): # Открываем аудиопоток с микрофона 
                while True:
                    data = self.audio_queue.get() # Забираем аудиоданные из очереди
                    # "Скармливаем" распознавателю
                    if self.recognizer.AcceptWaveform(data):
                        result = self.recognizer.Result() # Если распознана полная фраза, получаем результат
                        query = json.loads(result)["text"] # Извлекаем текст

                        # Если текст не пустой, кладем его в очередь команд
                        if query:
                            play_sfx('silent_execution')
                            publish(events.USER_SPEECH, query=query)
                            logger.info(f"[Vosk] Recognized: {query}")

