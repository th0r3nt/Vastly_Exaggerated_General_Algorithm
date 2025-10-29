# main.py
from assistant_tools.utils import play_sfx
import threading
import time
play_sfx('general_system_startup') # Для атмосферного звука вызываем ДО всех импортов

from assistant_brain.brain import initialize_brain, generate_general_greeting  # noqa: E402, F401
from assistant_brain.hotkeys_manager import initialize_hotkeys_manager  # noqa: E402
from assistant_output.voice_output_eng import SpeechModuleENG  # noqa: E402
from assistant_output.voice_output_rus import SpeechModuleRUS  # noqa: E402
from assistant_vector_database.database import initialize_database  # noqa: E402
from assistant_general.general_settings import choose_language  # noqa: E402

initialize_brain() # вызывает subscribe("USER_SPEECH", generate_response), чтобы не импортировать сразу весь brain
initialize_database()
initialize_hotkeys_manager()

def main(device_type):

    if device_type == "pc":
        while True: 
            print("\nPlease, choose language for V.E.G.A.")
            command = input("'1' - russian, '2' - english, '3' - exit \n\n>> ")

            if command == "1": # Если русский язык
                play_sfx("select")
                speech_module = SpeechModuleRUS()
                speech_module.start()
                choose_language("RUSSIAN")
                break

            if command == "2": # Если английский язык 
                play_sfx("select")
                speech_module = SpeechModuleENG()
                speech_module.start()
                choose_language("ENGLISH")
                break

            if command == "3":
                play_sfx("select")
                print("Exit from the V.E.G.A. system.")
                exit()

            else:
                play_sfx("unknown_command")
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
                play_sfx("select")
                print("Logout from the V.E.G.A. system")
                exit()

            else:
                play_sfx("unknown_command")
                print("Incorrect mode. Please try again.")


        # Уменьшать громкость остальных звуков на пк при речи Веги, чтобы её не перебивали (ЧЕРЕЗ EVENT_BUS, СОЗДАТЬ ОТДЕЛЬНОЕ СОБЫТИЕ ГЕНЕРАЦИИ РЕЧИ, ЧТОБЫ ВЫЗЫВАТЬ ФУНКЦИЮ УМЕНЬШЕНИЯ ВСЕХ ЗВУКОВ, КРОМЕ ВЕГИ)

        # Создать лист текущих задач для важных задач (по типу "Вега, мониторь этот сайт на предмет новой информации"), которая мониторится каждые n минут 

        try:
            while True:
                time.sleep(1)
                # Фоновые задачи
                # См. в assistant_background_tasks\\background_tasks.py

        except KeyboardInterrupt:
            print("\nThe program is ending.")

    elif device_type == "smartphone":
        print("Функция в разработке.")

if __name__ == "__main__":
    main("pc")