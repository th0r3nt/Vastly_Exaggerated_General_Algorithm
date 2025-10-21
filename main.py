# main.py
import threading
import time
from assistant_brain.brain import initialize_brain, generate_general_greeting  # noqa: F401
from assistant_brain.hotkeys_manager import initialize_hotkeys_manager
from assistant_output.voice_output_eng import SpeechModuleENG
from assistant_output.voice_output_rus import SpeechModuleRUS
from assistant_tools.utils import play_sfx
from assistant_vector_database.database import initialize_database
from assistant_general.general_settings import choose_language

play_sfx('hard_processing')

initialize_brain() # вызывает subscribe("USER_SPEECH", generate_response), чтобы не импортировать сразу весь brain
initialize_database()
initialize_hotkeys_manager()

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

generate_general_greeting() # Можно закомментировать, чтобы не мешало тестированию

# Потестить слегка обновленный промпт Веги. Если что убрать строчки про OS

# Создать функцию all_names_playlists (Передавает Веге названия всех плейлистов Foobar2000)
# создать функции list_all_memory_entries() и delete_memory_entry(id)
# Написать search_telegram_channels() - навык поиска телеграм каналов по ключевым словам 
# Настроить чертово логирование во ВСЕХ файлах, отправлять в них вопросы пользователя и ответы Веги
# Написать def detailed_weather_for_hour - для осадков на ближайший час (дождь, снег)

# Всё еще возвращает 
# 2025-10-21 04:21:36,930 - google_genai.types - [WARNING] - Warning: there are non-text parts in the response: ['function_call'], returning concatenated text result from text parts. Check the full candidates.content.parts accessor to get the full model response.
# Несмотря на то, что вносил правки. 

# ОБЯЗАТЕЛЬНО НЕ УДАЛЯТЬ ПРОШЛЫЕ ФРАЗЫ ИЗ КРАТКОВРЕМЕННОЙ ПАМЯТИ, КОТОРЫЕ ПЕРЕШЛИ ЧЕРТУ СКОЛЬЗЯЩЕГО ОКНА (по дефолту 50 сообщений) - они должны сохраняться в отдельный общий json
# Обаготить все кратковременные записи метаданными - когда было сказано, в каком контексте, какие действия предпринимались после этого (если предпринимались)
# Настроить так, чтобы при больших перерывах, больше 7 часов, к примеру, кратковременная память из тех самых 50 сообщений (не ОБЩАЯ, а именно та, которая передается Веге при всех запросах) удалялась.
# Перевести добавление записей на Event Bus

# В будущем добавить новые датчики для брифинга и простого приветствия
# Передавать в брифинг информацию о канале, например, количество подписчиков, последние посты и т.д. (можно также передавать прошлые наблюдения о канале, чтобы Вега могла анализировать динамику развития канала)

# Фоновое прослушивание всего окружающего звука, сделать навык, который возвращает последние фразы (последняя минута, например, дополнительно помечать, на какой секунде произошел звук (как раз тут можно потестировать разнование диалогов и отдельных людей/говорящих))

# НЕКОТОРЫЕ ФУНКЦИИ НЕ ИСПОЛЬЗУЮТ EVENT BUS, НО ДОЛЖНЫ ИСПОЛЬЗОВАТЬ (порассуждать)
# Поизучать Redis для кратковременной памяти 
# Изучить текущий Event Bus, зачем именно там нужен класс

# Прослушать из вк
# Все записи голоса
# Джарвис
# И в очередной раз вдохновиться диалогами

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


# Скачать Rammstein, Slaughter To Prevail, Disturbed, Three Days Grace, Linkin Park, System of a Down, Korn, Deftones в Foobar2000.
# Уменьшать громкость остальных звуков при речи Веги, чтобы её не перебивали

# Можно сделать так, что при копировании чего-то в буфер обмена, это будет озвучиваться и превращаться в файл mp3 (Некая "симуляция" голосовых сообщений, если Вега будет отправлять сообщения в мессенджерах)
# Настроить через EVENT_BUS а также обязательно удалять префикс [V.E.G.A.] 
# Думаю, будет интересным эффектом, когда моему собеседнику внезапно отвечает речь Веги (как раз для этого и создан assistant_temporary_files)

# Создать лист текущих задач для важных задач (по типу "Вега, мониторь этот сайт на предмет новой информации"), которая мониторится каждые n минут 

try:
    while True:
        time.sleep(1)
        # Фоновые задачи
        # См. в assistant_background_tasks\\background_tasks.py

except KeyboardInterrupt:
    print("\nThe program is ending.")

# Изменить _process_interaction
# Как в будущем может выглядеть кратковременная память (обагощенная метаданными):
# В дальнейшем получать данные через .get()

# [
#     {
#         "timestamp": "2025-10-20 18:44:20",
#         "actor": "User",
#         "input_type": "text",
#         "content": "Вега, напиши комментарий от своего имени для этого поста",
#         "triggered_action": {
#             "skill_name": "generate_comment",
#             "parameters": {
#                 "target_post_id": "12345",
#                 "persona": "V.E.G.A."
#             },
#             "output": "copy_to_clipboard"
#         }
#     },
#     {
#         "timestamp": "2025-10-20 18:44:20",
#         "actor": "V.E.G.A.",
#         "input_type": "generated_text",
#         "content": "Я сгенерировала комментарий, Сэр. Надеюсь, ваш контакт оценит пожелание стабилизации режима активности.",
#         "triggered_action": null
#     },
#     {
#         "timestamp": "2025-10-20 19:08:27",
#         "actor": "User",
#         "input_type": "text",
#         "content": "Кстати, запиши в память, что я планирую участвовать в НТО на момент записи.",
#         "triggered_action": {
#             "skill_name": "save_to_memory",
#             "parameters": {
#                 "text": "Пользователь планирует участвовать в НТО (Национальная Технологическая Олимпиада)."
#             },
#             "output": "database_write_success"
#         }
#     }
# ]