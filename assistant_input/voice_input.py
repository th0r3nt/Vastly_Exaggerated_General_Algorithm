# input.py
import threading
import vosk
import logging
import json
import sounddevice
import queue

print("\n")

class SpeechListener(threading.Thread):
    """Слушает речь пользователя и кладет в очередь"""
    def __init__(self):
        super().__init__()
        self.audio_queue = queue.Queue()
        self.daemon = True

        try: # Инициализация Vosk
            model_path = "vosk_model/vosk-model-small-ru-0.22" # Либо vosk-model-ru-0.42, либо vosk-model-small-ru-0.22
            self.model = vosk.Model(model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
            print("\nThe local speech recognition engine (Vosk) has been initialized successfully.")
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to initialize Vosk: {e}")
            self.recognizer = None

    def _audio_callback(self, indata, frames, time, status):
        """Единственная задача - складывать аудиоданные в очередь"""
        self.audio_queue.put(bytes(indata))

    def run(self):
        """Основной цикл потока-слушателя"""
        if not self.recognizer: # Если Vosk не инициализировался, поток просто завершает работу
            return
        
        else:
            from assistant_event_bus.event_bus import publish
            print("Listening Stream (Vosk): started.\n")
            with sounddevice.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=self._audio_callback): # Открываем аудиопоток с микрофона 
                while True:
                    data = self.audio_queue.get() # Забираем аудиоданные из очереди
                    # "Скармливаем" их распознавателю
                    if self.recognizer.AcceptWaveform(data):
                        result = self.recognizer.Result() # Если распознана полная фраза, получаем результат
                        query = json.loads(result)["text"] # Извлекаем текст

                        # Если текст не пустой, кладем его в очередь команд
                        if query:
                            print(f"[Vosk] Recognized: {query}")
                            publish("USER_SPEECH", query=query)
                            logging.info(f"[Vosk] Recognized: {query}")

