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
            

try:
    while True:
        time.sleep(1)
        #TODO: Сделать фоновые задачи, по типу напоминания о разминке или случайных комментариев/интересных фактов.
except KeyboardInterrupt:
    print("\nThe program is ending.")
