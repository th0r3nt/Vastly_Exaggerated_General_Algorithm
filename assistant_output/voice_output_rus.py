# voice_output_rus.py

import threading
import queue
import sounddevice as sd
import soundfile as sf
from edge_tts import Communicate
# from assistant_event_bus.event_bus import subscribe
import os 

class SpeechModuleRUS:
    def __init__(self):
        self.worker_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.tts_queue = queue.Queue()
        
        self.temp_folder = "assistant_temporary_files"
        os.makedirs(self.temp_folder, exist_ok=True)
        
        # subscribe("GEMINI_RESPONSE", self.queue_text_for_synthesis)
        print("The speech module has been initialized.")

    def synth(self, text: str, voice: str = "ru-RU-SvetlanaNeural"):
        """Синтезирует text, сохраняет его во временный файл и воспроизводит."""
        
        output_filename = "vega_speech.mp3"
        full_path = os.path.join(self.temp_folder, output_filename)
        
        communicate = Communicate(text, voice)
        
        def save_and_play():
            # Используем полный путь ---
            communicate.save_sync(full_path)
            data, samplerate = sf.read(full_path)
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

if __name__ == "__main__":
    test = SpeechModuleRUS()
    test.start()

    test.synth(text="Проверка")