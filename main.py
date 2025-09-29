# main.py
from assistant_brain.brain import initialize_brain, generate_greetings
from assistant_output.output import SpeechModule
import threading
import time
from assistant_tools.utils import play_sfx
from assistant_vector_database.database import initialize_database

play_sfx('hard_processing')

initialize_brain() # вызывает subscribe("USER_SPEECH", generate_response), чтобы не импортировать сразу весь brain
speech_module = SpeechModule() # вызывает subscribe("GEMINI_RESPONSE", generate_output)
speech_module.start()
initialize_database()
generate_greetings()

while True: 
    input_mode = input("\nSelect input mode (1 - Voice, 2 - Text, 3 - Exit): ")
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
        print("Exit from the V.E.G.A. system.")
        exit()

    else:
        print("Invalid mode. Please try again.")

try:
    while True:
        time.sleep(1)
        #TODO: Сделать фоновые задачи, по типу напоминания о разминке или случайных комментариев/интересных фактов.
except KeyboardInterrupt:
    print("\nThe program is ending.")


