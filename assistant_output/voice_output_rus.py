# voice_output_rus.py

import threading
import queue
import sounddevice as sd
import soundfile as sf  # 
from edge_tts import Communicate
from assistant_event_bus.event_bus import subscribe

class SpeechModuleRUS:
    def __init__(self):
        self.worker_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.tts_queue = queue.Queue()
        subscribe("GEMINI_RESPONSE", self.queue_text_for_synthesis)
        print("The speech module has been initialized.")

    # Добавлен 'self' как первый аргумент
    def synth(self, text: str, voice: str = "ru-RU-SvetlanaNeural", outfile: str = "output.mp3"):
        """Синтезирует text, сохраняет в outfile и воспроизводит его."""
        # Создаем Communicate асинхронно, чтобы избежать блокировок
        communicate = Communicate(text, voice)
        
        def save_and_play():
            communicate.save_sync(outfile)
            data, samplerate = sf.read(outfile)
            sd.play(data, samplerate)
            sd.wait() 
        save_and_play()

    def start(self):
        """Запускает фоновый поток для обработки очереди."""
        self.worker_thread.start()

    def _tts_worker(self):
        """
        Работает в фоновом потоке, берет текст из очереди и озвучивает его.
        """
        while True:
            try:
                text_to_speak = self.tts_queue.get()
                if text_to_speak is None:
                    break
                self.synth(text=text_to_speak, voice="ru-RU-SvetlanaNeural")
                self.tts_queue.task_done()

            except Exception as e:
                print(f"Критическая ошибка в потоке озвучивания: {e}")

    def queue_text_for_synthesis(self, **kwargs):
        """
        Публичный метод, который вызывается по событию.
        Добавляет текст в очередь на озвучивание.
        """
        text = kwargs.get('text')
        if text and isinstance(text, str):
            self.tts_queue.put(text)