# main.py
from assistant_brain.brain import initialize_brain, generate_greetings
from assistant_output.voice_output_eng import SpeechModuleENG
from assistant_output.voice_output_rus import SpeechModuleRUS
import threading
import time
from assistant_tools.utils import play_sfx
from assistant_vector_database.database import initialize_database

play_sfx('hard_processing')

initialize_brain() # вызывает subscribe("USER_SPEECH", generate_response), чтобы не импортировать сразу весь brain
initialize_database()

while True: 
    print("\nPlease, choose language for V.E.G.A.")
    command = input("'1' - russian, '2' - english, '3' - exit \n\n>> ")

    if command == "1": # Если русский язык
        speech_module = SpeechModuleRUS()
        speech_module.start()
        break

    if command == "2": # Если английский язык 
        speech_module = SpeechModuleENG()
        speech_module.start()
        break

    if command == "3":
        print("Exit from the V.E.G.A. system.")
        exit()

    else:
        print("Invalid mode. Please try again.")

generate_greetings()

while True:
    input_mode = input("\nSelect the input mode ('1' - voice, '2' - text, '3' - output): ")
    if input_mode == "1":
        from assistant_input.voice_input import SpeechListener
        play_sfx("select")
        speech_listener = SpeechListener()
        speech_listener.start()
        break 

    elif input_mode == "2":
        from assistant_input.text_input import text_input_loop
        play_sfx("select")
        text_thread = threading.Thread(target=text_input_loop)
        text_thread.daemon = True
        text_thread.start()
        break 

    elif input_mode == "3":
        print("Logout from the V.E.G.A. system")
        exit()

    else:
        print("Incorrect mode. Please try again.")


# def generate_briefing(assistant):
#     """Генерирует и озвучивает утренний/дневной брифинг."""
            

try:
    while True:
        time.sleep(1)
        #TODO: Сделать фоновые задачи, по типу напоминания о разминке или случайных комментариев/интересных фактов.

        # 1. Системный мониторинг (def system_monitor):    YES 
        # Что делает: Каждые 5 секунд проверяет состояние ПК: загрузку CPU, использование RAM и GPU, температуру процессора, свободное место на дисках.

        # 2. Сетевой мониторинг (network_monitor.py):      NO 
        # Что делает: Периодически пингует ключевые ресурсы (например, Google DNS 8.8.8.8) для проверки статуса интернет-соединения. Измеряет скорость скачивания/отдачи.

        # 3. Парсинг новостей/данных (data_harvester.py):
        #Что делает: Раз в час "ходит" на выбранные тобой сайты (новостные агрегаторы, Reddit, Hacker News, GitHub Trending) и собирает заголовки по ключевым для тебя темам (AI, Python, кибербезопасность, квантовая физика).

        # 4. Анализ погоды (weather_agent.py):
        # Что делает: Через API погоды (например, OpenWeatherMap) проверяет прогноз на сегодня и завтра.

        # 5. Анализ паттернов использования ПК (usage_analyzer.py):
        # Что делает: Логирует, какие приложения ты запускаешь и в какое время. Со временем она сможет находить паттерны.

        # 6. Автоматизация рутины (task_automator.py):
        # Что делает: Выполняет простые скрипты по расписанию или триггеру. Например, в полночь запускает скрипт для очистки временных файлов или создания бэкапа важных папок.

        # 7. Генератор случайных взаимодействий (serendipity_engine.py):
        # Что делает: Это реализация TODO. В случайные моменты времени (не чаще раза в час, чтобы не раздражать) Вега выдает что-то не связанное с работой:
        # Интересный факт: "Знаете ли вы, что в момент Большого взрыва Вселенная была горячее, чем ядро Солнца, и имела плотность, превышающую плотность атомного ядра?"
        # "Анализ вашего плейлиста показывает 87% совпадение с 'грустными песнями для одиноких вечеров'. Система работает в штатном режиме."
        # "Если бы вы могли добавить мне одну новую способность прямо сейчас, что бы это было?"

        # 8. Умный буфер обмена (clipboard_manager.py):
        # Что делает: Вега постоянно мониторит буфер обмена. Если она видит, что скопировано что-то, похожее на ссылку, она может спросить: "Хотите, я открою эту ссылку в браузере?". Если это кусок кода, она может предложить его отформатировать. Если это математическое выражение, она может его вычислить.

        # 9. Агент по управлению файлами (file_organizer.py):
        # Что делает: Раз в день сканирует папку "Загрузки". Если находит файлы старше, скажем, 30 дней, предлагает их удалить или архивировать. Может сортировать файлы по типам в соответствующие папки (картинки в "Изображения", документы в "Документы").

        # 10. Синхронизация между устройствами (def sync_clipboard):
        # Что делает: Если скопирован текст на ПК, Вега может отправить его на твой телефон (через Telegram-бота или Pushbullet). Или наоборот. Может синхронизировать открытые вкладки или списки дел.

        # 12. Абстрактор научных статей (arxiv_abstractor.py):
        # Что делает: Вега мониторит репозиторий научных препринтов arXiv.org по ключевым словам (Quantum Physics, AGI, etc.). Когда появляется новая интересная статья, она не просто дает ссылку, а пытается прочитать аннотацию (abstract) и выделить главную идею в одном предложении.

        # 13. Системный мониторинг в реальном времени
        # Как это работает: Вместо того чтобы Вега просто говорила "Загрузка CPU 75%", она в реальном времени строит и обновляет линейный график, показывающий динамику загрузки CPU за последние 60 секунд.

except KeyboardInterrupt:
    print("\nThe program is ending.")
