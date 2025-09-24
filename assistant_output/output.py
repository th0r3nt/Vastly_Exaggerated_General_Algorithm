# output.py
import queue
import threading
import sounddevice as sd  # Возвращаем sounddevice
from kokoro import KPipeline
from assistant_event_bus.event_bus import subscribe

# Kokoro генерирует аудио с частотой 24000 Гц. Это важно указать.
SAMPLE_RATE = 24000

class SpeechModule:
    """
    Класс, отвечающий за синтез и воспроизведение речи.
    Работает асинхронно через очередь и фоновый поток.
    Воспроизводит аудио напрямую из памяти, без временных файлов.
    """
    def __init__(self, lang_code: str = 'b', voice: str = 'bf_lily'):
        try:
            # Проверим, есть ли доступные аудиоустройства
            sd.query_devices()
        except Exception as e:
            print(f"КРИТИЧЕСКАЯ ОШИБКА: Не найдено аудиоустройство вывода. {e}")
            # В реальном приложении здесь можно было бы завершить работу или отключить модуль
            return

        self.pipeline = KPipeline(lang_code=lang_code)
        self.voice = voice
        self.tts_queue = queue.Queue()
        
        subscribe("GEMINI_RESPONSE", self.queue_text_for_synthesis)
        
        self.worker_thread = threading.Thread(target=self._tts_worker, daemon=True)
        print("The speech module has been initialized.")

    def start(self):
        """Запускает фоновый поток для обработки очереди."""
        self.worker_thread.start()

    def _synthesize_and_play(self, text: str):
        """
        Генерирует речь и воспроизводит аудио-сегменты напрямую.
        """
        try:
            generator = self.pipeline(text, voice=self.voice)
            for _, _, audio_chunk in generator:
                # audio_chunk - это и есть NumPy массив, который нам нужен
                sd.play(audio_chunk, SAMPLE_RATE)
                sd.wait()  # Ждем, пока текущий кусок аудио доиграет
        except Exception as e:
            print(f"Ошибка во время синтеза или воспроизведения речи: {e}")

    def _tts_worker(self):
        """
        Работает в фоновом потоке, берет текст из очереди и озвучивает его.
        """
        while True:
            try:
                text_to_speak = self.tts_queue.get()
                if text_to_speak is None:
                    break
                
                self._synthesize_and_play(text_to_speak)
                
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