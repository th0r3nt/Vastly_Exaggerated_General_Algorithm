# brain.py
import google.generativeai as genai
from google import genai  # noqa: F811
from google.genai import types
import threading
import os
import json
import datetime
from collections import deque
import logging
from dotenv import load_dotenv
from assistant_event_bus.event_bus import subscribe, publish
from assistant_tools.utils import play_sfx
import assistant_general.general_settings as general_settings
from assistant_general.general_tools import read_json, write_json
from assistant_brain.added_skills import function_declarations, skills_registry # ДОБАВЛЯТЬ НОВЫЕ УМЕНИЯ В ЭТОТ ФАЙЛ
from assistant_general.logger_config import setup_logger
from assistant_tools.skills import get_screenshot_context, get_time_and_date
from assistant_event_bus import event_definitions as events

setup_logger()
logger = logging.getLogger(__name__)

load_dotenv() # для загрузки API ключей из .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
tools = types.Tool(function_declarations=function_declarations)
config = types.GenerateContentConfig(tools=[tools])

# Загружаем при краткосрочную память диалогов (скользящее окно)
try:
    with open(general_settings.SHORT_TERM_MEMORY_PATH, 'r', encoding='utf-8') as f:
        short_term_memory_list = json.load(f) # Загружаем как обычный список
        logger.debug("File 'short_term_memory.json' opened successfully.")
except (FileNotFoundError, json.JSONDecodeError):
    logger.info("The file 'short_term_memory.json' either does not exist or is of the wrong format. A new one is being created.")
    play_sfx("error")
    short_term_memory_list = []

# Загружаем при старте полную историю диалогов
try:
    with open(general_settings.ALL_HISTORY_OF_DIALOGUES_PATH, 'r', encoding='utf-8') as f:
        all_history_of_dialogues = json.load(f) # Загружаем как обычный список
        logger.debug("File 'all_history_of_dialogues.json' opened successfully.")
except (FileNotFoundError, json.JSONDecodeError):
    logger.info("The file 'all_history_of_dialogues.json' either does not exist or is of the wrong format. A new one is being created.")
    play_sfx("error")
    all_history_of_dialogues = []

short_term_memory = deque(short_term_memory_list, maxlen=general_settings.MAX_MEMORY) # Оборачиваем кратковременную память в deque с лимитом
# А полная история остается обычным списком

def _save_all_memory():
    """Единая функция для сохранения диалогов в кратковременную и общую память."""
    try:
        # Сохраняем кратковременную память
        with open(general_settings.SHORT_TERM_MEMORY_PATH, 'w', encoding='utf-8') as f:
            json.dump(list(short_term_memory), f, indent=4, ensure_ascii=False)
        
        # Сохраняем полную историю
        with open(general_settings.ALL_HISTORY_OF_DIALOGUES_PATH, 'w', encoding='utf-8') as f:
            json.dump(all_history_of_dialogues, f, indent=4, ensure_ascii=False) # all_history_of_dialogues - это уже список
            
    except Exception as e:
        logger.error(f"Error saving files to memory: {e}")
        play_sfx("error")

def add_entry_to_memory(actor: str, content: str, triggered_action: dict = None):
    """Универсальная функция для добавления одной записи в обе версии памяти и их сохранения."""
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_entry = {
        "timestamp": current_date,
        "actor": actor,
        "content": content,
        "triggered_action": triggered_action
    }

    # Обновляем обе структуры в оперативной памяти
    logger.debug(new_entry)
    short_term_memory.append(new_entry)
    all_history_of_dialogues.append(new_entry)

    # Вызываем сохранение на диск
    _save_all_memory()

def _run_gemini_task(**kwargs):
    """Срабатывает, когда пользователь говорит с Вегой в обычном диалоге. Передается запрос пользователя + память из базы данных, дальше формулируется запрос к Gemini с Function Calling."""
    play_sfx("execution")
    query = kwargs.get('query') # Также передает время обращения (по формату Year-Month-Day Hour-Minute-Secord) вместе с запросом 
    database_context = kwargs.get('database_context')
    img = kwargs.get("img", None)

    add_entry_to_memory(actor="User", content=query) # Добавляем запись о запросе пользователя в память

    try:
        initial_contents = [
            general_settings.VEGA_PERSONALITY_CORE,
            f"""
            Сейчас твоя задача — поддерживать разговор.

            Не отступай от своей индивидуальности. Твоё имя женское.

            Вот соответствующая информация из вашей базы данных (памяти). Используйте её, чтобы дать наиболее полный ответ. Если информация нерелевантна, можете её проигнорировать.
            {database_context}

            Вот предыдущий диалог (полезно для контекста):
            {list(short_term_memory)}

            Запрос пользователя (с основного пк): {query}
            """
        ] # {list(short_term_memory)} - list(...) важен, так как без него будет передаваться нейросети сама строка "deque([ {..}, {..} ], maxlen=26)", что засоряет контекст. С list(...) будет чище - "[ {..}, {..} ]"

        # Добавляем изображение, только если оно было успешно создано
        if img:
            initial_contents.append(img)

        # Отправляем первый запрос
        response = client.models.generate_content(
            model=general_settings.MODEL_GEMINI,
            contents=initial_contents,
            config=config,
        )

        function_calls = False
        results_of_tool_calls = []
        text_parts = []
        
        # Запоминаем историю первого ответа для второго запроса
        history = response.candidates[0].content

        triggered_action_data = None # Сохраняем информацию о вызванной функции для записи в память диалогов

        # Проверяем наличие вызовов Function Calling
        for part in history.parts:
            if hasattr(part, 'function_call') and part.function_call is not None:
                function_call = part.function_call
                print(f"\nFunction to call: {function_call.name}")
                print(f"Arguments: {function_call.args}\n")

                function_calls = True

                # Сохраняем информацию о ПЕРВОМ вызове функции для лога
                if not triggered_action_data:
                    triggered_action_data = {
                        "skill_name": function_call.name,
                        "parameters": dict(function_call.args) # Преобразуем args в обычный dict
                    }

                function_to_call = skills_registry[function_call.name]
                result = function_to_call(**function_call.args)

                function_response_part = types.Part(
                    function_response=types.FunctionResponse(
                        name=function_call.name,
                        response={'result': result}
                    )
                )
                results_of_tool_calls.append(function_response_part)

            if hasattr(part, 'text'):
                text_parts.append(part.text)

        final_text = None
        if function_calls:
            # Передаем всё: личность, историю, результаты и СНОВА скриншот
            follow_up_contents = [
                general_settings.VEGA_PERSONALITY_CORE, 
                history, 
                *results_of_tool_calls
            ]
            if img:
                follow_up_contents.append(img)

            final_response = client.models.generate_content(
                model=general_settings.MODEL_GEMINI,
                contents=follow_up_contents,
                config=config,
            )
            # Надежно извлекаем текст из финального ответа
            final_text_parts = []
            for part in final_response.candidates[0].content.parts:
                if hasattr(part, 'text'):
                    final_text_parts.append(part.text)
            final_text = "".join(final_text_parts)

        else:
            final_text = "".join(text_parts)

        if final_text: # Проверка правильно ловит None, и "" в случае, если нейросеть ответит молчанием
            final_text_to_publish = final_text.replace("*", "").replace("#", "").replace("V.E.G.A.", "VEGA").replace("&", "and")
        else:
            final_text_to_publish = "Выполнено, Сэр." # Безопасный ответ-заглушка

        final_text_to_publish = final_text_to_publish.replace("*", "").replace("#", "").replace("V.E.G.A.", "VEGA").replace("&", "and")
        
        play_sfx("execution")
        print(f"V.E.G.A.: {final_text_to_publish}")
        publish(events.GEMINI_RESPONSE, text=final_text_to_publish)
        
        # Добавляем запись об ответе Веги в память, включая triggered_action
        add_entry_to_memory(actor="V.E.G.A.", content=final_text_to_publish, triggered_action=triggered_action_data)

    except Exception as e:
        play_sfx("error")
        logger.error(f"Error when addressing Gemini API: {e}")
        add_entry_to_memory(actor="System", content=f"Error during Gemini task: {e}") # Логируем ошибку в память

def generate_response(*args, **kwargs):
    """Принимает запрос пользователя + контекст из векторной базы данных, делает контекстный скриншот и вызывает _run_gemini_task, передавая необходимые данные в ОТДЕЛЬНОМ ПОТОКЕ."""
    if not args:
        logger.error("*args not found")
        play_sfx("silent_error")
        return
    
    data_package = args[0] # Нужен весь словарь целиком
    
    # Когда у нас есть словарь, достаем из него данные по ключам
    current_time = get_time_and_date()
    query = data_package.get('original_query')
    final_query = f"{current_time}: {query}"
    database_context = data_package.get('database_context')

    if not query:
        print("Query not found")
        return
    
    image_context = get_screenshot_context() # Получаем в контекст изображение экрана

    play_sfx('silent_execution')

    worker_thread = threading.Thread(
        target=_run_gemini_task, 
        kwargs={"query": final_query, "database_context": database_context, "img": image_context}
    )
    worker_thread.start()

    print("\nThe task for Gemini has been sent to the background.")

def generate_general_greeting():
    """Генерирует приветствие при любом запуске Веги. Если Вега запущена впервые за день: проводит утренний брифинг; иначе стандартно приветствует."""
    tasks_file = general_settings.TASKS_COMPLETED_FILE_PATH
    tasks_completed_today = read_json(tasks_file) # Читаем файл с выполненными задачами

    now = datetime.datetime.now()
    today_date_str = now.strftime("%Y-%m-%d") # Результат в формате: "2025-10-17"
    current_hour = now.hour  # Получаем час как int, чтобы лучше сравнить с BRIEFING_START_HOUR: если текущий час больше, чем, к примеру, 5 часов утра, то стоит провести брифинг
    last_briefing_date_str = tasks_completed_today.get('last_briefing_date', None) # Получаем дату, когда последний раз был проведен брифинг

    image_context = get_screenshot_context() # Получаем в контекст изображение экрана

    add_entry_to_memory(actor="System", content="User activated the system.")

    if last_briefing_date_str != today_date_str and current_hour >= general_settings.BRIEFING_START_HOUR: # Сравнивает текущую дату и дату в 'last_briefing_date': если даты разные - СЛЕДУЕТ ПРОВЕСТИ БРИФИНГ
        try:
            print("Generating a briefing.")
            from assistant_tools.skills import get_weather, get_habr_news
            from assistant_vector_database.database import vectorstore

            # Собираем данные для брифинга
            current_time = get_time_and_date()
            weather_data = get_weather() # Получаем погоду
            habr_news = get_habr_news(limit=general_settings.NUM_OF_NEWS_IN_BRIEFING) # Получаем свежие новости
            memory_database = vectorstore.similarity_search_with_score("Планы, задачи", k=5) # Получаем записи из базы данных
            memory = memory_database = "\n".join([record.page_content for record, score in memory_database]) # Сортируем в красивую строку, можно добавить if score <= general_settings.SIMILARITY_THRESHOLD если в базу данных попадается шелуха
            logger.debug(f"Записи в датабазе для утреннего брифинга: {memory}")

            initial_contents = [
            general_settings.VEGA_PERSONALITY_CORE + f"""
            Директива: Утренний брифинг. Первая активация.

            Сэр вернулся в сеть. Проанализируй предоставленные ниже оперативные данные и подготовь для него единую, связную сводку о текущей обстановке. Твоя задача — выделить главное, отсечь шум и доложить то, что действительно имеет значение.

            Действуй в рамках своей личности: аналитично, сжато, с долей профессионального сарказма.

            Вот необработанные данные для анализа:
            Текущее время и дата: {current_time}
            Текущая погода в Липецке: {weather_data};
            Текущие новости с Хабра: {habr_news};
            Данные из вашей памяти (можете пропустить, если там нет ничего полезного): {memory}


            Вот предыдущий диалог (может быть полезен для контекста):
            {list(short_term_memory)}
            """
            ]
            # Добавляем изображение, только если оно было успешно создано
            if image_context:
                initial_contents.append(image_context)

            # Отправляем первый запрос
            response = client.models.generate_content(
                model=general_settings.MODEL_GEMINI,
                contents=initial_contents,
                config=config,
            )


            # Собираем текстовые части, чтобы избежать предупреждения
            text_parts = []

            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text'):
                    text_parts.append(part.text)
            
            greeting_text = "".join(text_parts)

            play_sfx("system_startup")
            print(f"V.E.G.A. (briefing): {greeting_text}")
            publish(events.GEMINI_RESPONSE, text=greeting_text)

            # Добавляем в память
            add_entry_to_memory(actor="V.E.G.A.", content=greeting_text)


            tasks_completed_today['last_briefing_date'] = today_date_str # Меняем дату последнего брифинга на сегодня
            write_json(tasks_file, tasks_completed_today)

        except Exception as e:
            play_sfx("error")
            print(f"Error when addressing Gemini API: {e}")
            logger.error(f"Error when addressing Gemini API: {e}")
        
    else: # ЕСЛИ ЗАПУСК НЕ ПЕРВЫЙ ЗА ДЕНЬ ИЛИ ЧАС МЕНЬШЕ УСТАНОВЛЕННОГО - СТАНДАРТНОЕ ПРИВЕТСТВИЕ
        print("Generating a standard greeting protocol.")
        current_time = get_time_and_date()
        try:
            initial_contents = [
            general_settings.VEGA_PERSONALITY_CORE + f"""
            Вот предыдущий диалог (полезно для контекста):

            {list(short_term_memory)}

            Сэр только что снова запустил вас сегодня. Текущее время: {current_time}.

            Твоя задача — поприветствовать его. Твоё приветствие должно быть персонализированным и в твоем стиле.

            Сохраняй личный тон.
            Сохраняй тон кратким, деловым и саркастическим, как у Джарвиса. Ваше имя женское.
            """
            ]
            # Добавляем изображение, только если оно было успешно создано
            if image_context:
                initial_contents.append(image_context)

            # Отправляем первый запрос
            response = client.models.generate_content(
                model=general_settings.MODEL_GEMINI,
                contents=initial_contents,
                config=config,
            )
            
            # Собираем текстовые части, чтобы избежать предупреждения
            text_parts = []

            for part in response.candidates[0].content.parts:
                if hasattr(part, 'text'):
                    text_parts.append(part.text)
            
            greeting_text = "".join(text_parts)

            play_sfx("system_startup")
            print(f"V.E.G.A.: {greeting_text}")
            publish(events.GEMINI_RESPONSE, text=greeting_text)

            # Добавляем в память
            current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            add_entry_to_memory(f"{current_date}; User activated the system.")
            add_entry_to_memory(f"{current_date}; V.E.G.A.: {greeting_text}") 

        except Exception as e:
            play_sfx("error")
            print(f"Error when addressing Gemini API: {e}")
            logger.error(f"Error when addressing Gemini API: {e}")

def analysis_screen():
    """По горячей клавише (по умолчанию - 'ctrl+alt+shift+f1') вызывает Вегу и говорит ей, что нужно анализировать экран (для помощи в чем-то)."""
    print("Screen analysis has been called.")
    add_entry_to_memory(actor="User", content="[Hotkey pressed for screen analysis]")
    img = get_screenshot_context()
    current_time = get_time_and_date()
    try:
        initial_contents = [
            general_settings.VEGA_PERSONALITY_CORE,
            f"""
            Директива: "Что опять?". 
            Текущее время: {current_time}

            Сэр вызвал тебя по горячей клавише, передав изображение, надеясь на твоё содействие в том, что находится на экране. 
            Проанализируй ситуацию и действуй.

            Вот лог предыдущего диалога (он может предоставить полезный контекст):
            {list(short_term_memory)}
            """
        ]

        # Добавляем изображение, только если оно было успешно создано
        if img:
            initial_contents.append(img)

        play_sfx("execution")

        # Отправляем первый запрос
        response = client.models.generate_content(
            model=general_settings.MODEL_GEMINI,
            contents=initial_contents,
            config=config,
        )

        function_calls = False
        results_of_tool_calls = []
        text_parts = []
        
        # Запоминаем историю первого ответа для второго запроса
        history = response.candidates[0].content

        triggered_action_data = None # По аналогии с _run_gemini_task

        # Проверяем наличие вызовов Function Calling
        for part in history.parts:
            if hasattr(part, 'function_call') and part.function_call is not None:
                function_call = part.function_call
                print(f"\nFunction to call: {function_call.name}")
                print(f"Arguments: {function_call.args}\n")

                function_calls = True

                function_to_call = skills_registry[function_call.name]
                result = function_to_call(**function_call.args)

                function_response_part = types.Part(
                    function_response=types.FunctionResponse(
                        name=function_call.name,
                        response={'result': result}
                    )
                )
                results_of_tool_calls.append(function_response_part)

                if not triggered_action_data:
                    triggered_action_data = {
                        "skill_name": function_call.name,
                        "parameters": dict(function_call.args)
                    }

            if hasattr(part, 'text'):
                text_parts.append(part.text)

        if function_calls:
            # Передаем всё: личность, историю, результаты и СНОВА скриншот
            follow_up_contents = [
                general_settings.VEGA_PERSONALITY_CORE, 
                history, 
                *results_of_tool_calls
            ]
            if img:
                follow_up_contents.append(img)

            final_response = client.models.generate_content(
                model=general_settings.MODEL_GEMINI,
                contents=follow_up_contents,
                config=config,
            )
            final_text_to_publish = final_response.text
        else:
            final_text_to_publish = "".join(text_parts)

        final_text_to_publish = final_text_to_publish.replace("*", "").replace("#", "").replace("V.E.G.A.", "VEGA").replace("&", "and")
        
        play_sfx("execution")
        print(f"V.E.G.A.: {final_text_to_publish}")
        publish(events.GEMINI_RESPONSE, text=final_text_to_publish)

        # Добавляем в память
        add_entry_to_memory(actor="V.E.G.A.", content=final_text_to_publish)

    except Exception as e:
        play_sfx("error")
        logger.error(f"Error when addressing Gemini API: {e}")

def initialize_brain():
    """Подписывается на события, указывает, что применять при появлении этого события."""
    subscribe(events.USER_SPEECH_AND_RECORDS_FOUND_IN_DB, generate_response)
    subscribe(events.HOTKEY_ANALYSIS_TRIGGERED, analysis_screen)
