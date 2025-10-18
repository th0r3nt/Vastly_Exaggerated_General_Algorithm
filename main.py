# main.py
import threading
import time
from assistant_brain.brain import initialize_brain, generate_general_greeting
from assistant_output.voice_output_eng import SpeechModuleENG
from assistant_output.voice_output_rus import SpeechModuleRUS
from assistant_tools.utils import play_sfx
from assistant_vector_database.database import initialize_database
from assistant_general.general_settings import choose_language

play_sfx('hard_processing')

initialize_brain() # вызывает subscribe("USER_SPEECH", generate_response), чтобы не импортировать сразу весь brain
initialize_database()

while True: 
    print("\nPlease, choose language for V.E.G.A.")
    command = input("'1' - russian, '2' - english, '3' - exit \n\n>> ")

    if command == "1": # Если русский язык
        speech_module = SpeechModuleRUS()
        speech_module.start()
        choose_language("RUSSIAN")
        break

    if command == "2": # Если английский язык 
        speech_module = SpeechModuleENG()
        speech_module.start()
        choose_language("ENGLISH")
        break

    if command == "3":
        print("Exit from the V.E.G.A. system.")
        exit()

    else:
        print("Invalid mode. Please try again.")

generate_general_greeting()

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

      
try:
    while True:
        time.sleep(1)

        # Парсинг новостей/данных (data_harvester.py):
        #Что делает: Раз в час "ходит" на выбранные сайты (новостные агрегаторы, Reddit, Hacker News, GitHub Trending) и собирает заголовки по ключевым темам (AI, Python, кибербезопасность, квантовая физика)

        # Для фоновых задач:

        # Анализ погоды (weather_agent.py)
        # Что делает: Через API погоды (например, OpenWeatherMap) проверяет прогноз на сегодня и завтра

        # Генератор случайных взаимодействий (serendipity_engine.py):
        # Что делает: Это реализация TODO. В случайные моменты времени (не чаще раза в час, чтобы не раздражать) Вега выдает что-то не связанное с работой
        # Интересный факт: "Знаете ли вы, что в момент Большого взрыва Вселенная была горячее, чем ядро Солнца, и имела плотность, превышающую плотность атомного ядра?"
        # "Анализ вашего плейлиста показывает 87% совпадение с 'грустными песнями для одиноких вечеров'. Система работает в штатном режиме."
        # "Если бы вы могли добавить мне одну новую способность прямо сейчас, что бы это было?"

        # Системный мониторинг в реальном времени
        # Вместо того чтобы Вега просто говорила "Загрузка CPU 75%", она в реальном времени строит и обновляет линейный график, показывающий динамику загрузки CPU за последние 60 секунд

except KeyboardInterrupt:
    print("\nThe program is ending.")
