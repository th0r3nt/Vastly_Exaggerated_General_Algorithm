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
from assistant_tools.skills import get_screenshot_context, get_time, get_date, get_habr_news, get_processes, get_system_volume

setup_logger()
logger = logging.getLogger(__name__)

load_dotenv() # для загрузки API ключей из .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
tools = types.Tool(function_declarations=function_declarations)
config = types.GenerateContentConfig(tools=[tools])

try:
    with open(general_settings.SHORT_TERM_MEMORY_PATH, 'r', encoding='utf-8') as f:
        short_term_memory = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    print("Файла 'short_time_memory.ison' либо не существует, либо неверного формата. Создается новый в папку 'assistant_brain'.")
    # Если файла нет или он испорчен
    short_term_memory = []

def save_memory():
    with open(general_settings.SHORT_TERM_MEMORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(list(short_term_memory), f, indent=4, ensure_ascii=False) # ensure_ascii чтобы русский текст от пользователя записывался корректно

short_term_memory = deque(short_term_memory, maxlen=general_settings.MAX_MEMORY) # Применяем deque к загруженному списку, чтобы снова включить лимит

def _process_interaction(query, final_text_to_publish):
    """Сохраняет запрос пользователя и ответ Веги в кратковременную память, записывая конкретное  время общения."""
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    short_term_memory.append(f"{current_date}, User: {query}")
    short_term_memory.append(f"{current_date}, V.E.G.A.: {final_text_to_publish}")
    save_memory() # Важно: Сохранять нужно либо после каждого добавления, либо при завершении программы

def _run_gemini_task(**kwargs):
    query = kwargs.get('query')
    database_context = kwargs.get('database_context')
    img = kwargs.get("img", None)
    try:
        initial_contents = [
            general_settings.VEGA_PERSONALITY_CORE,
            f"""Right now, your task is to maintain a conversation. 
            Don't deviate from your personality. Your name is feminine.

            Here's the relevant information from your database (memory). Use it to provide the most complete answer. If the information is irrelevant, you can ignore it.
            {database_context}

            Here's the previous dialogue (useful for context):
            {short_term_memory}

            User request: {query}
            V.E.G.A: 
            """
        ]
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

        print(f"V.E.G.A.: {final_text_to_publish}")
        publish("GEMINI_RESPONSE", text=final_text_to_publish)
        _process_interaction(query, final_text_to_publish)

    except Exception as e: # Более общее исключение
        print(f"Error when addressing Gemini API: {e}")

def generate_response(*args, **kwargs):
    """Принимает запрос пользователя, контекст из векторной базы данных, делает контекстный скриншот и вызывает _run_gemini_task, передавая необходимые данные в ОТДЕЛЬНОМ ПОТОКЕ."""
    if not args:
        print("*args not found")
        return
    
    data_package = args[0] # Нужен весь словарь целиком
    
    # Когда у нас есть словарь, достаем из него данные по ключам
    query = data_package.get('original_query')
    database_context = data_package.get('database_context')

    if not query:
        print("Query not found")
        return
    
    image_context = get_screenshot_context() # Получаем в контекст изображение экрана

    worker_thread = threading.Thread(
        target=_run_gemini_task, 
        kwargs={"query": query, "database_context": database_context, "img": image_context}
    )
    worker_thread.start()

    print("\n[Brain] The task for Gemini has been sent to the background.")

def initialize_brain():
    """Подписывается на событие обнаруженной речи (или текстового запроса) от пользователя, указывает, что применять при появлении этого события."""
    subscribe("USER_SPEECH_AND_RECORDS_FOUND_IN_DB", generate_response)

def generate_general_greeting():
    """Генерирует приветствие при любом запуске Веги. Если Вега запущена впервые за день: проводит утренний брифинг; иначе стандартно приветствует."""
    tasks_file = "assistant_background_tasks\\tasks_completed_today.json"
    tasks_completed_today = read_json(tasks_file) # Читаем файл с выполненными задачами

    now = datetime.datetime.now()
    today_date_str = now.strftime("%Y-%m-%d") # Результат в формате: "2025-10-17"
    current_hour = now.hour  # Получаем час как int, чтобы лучше сравнить с BRIEFING_START_HOUR: если текущий час больше, чем, к примеру, 5 часов утра, то стоит провести брифинг
    last_briefing_date_str = tasks_completed_today.get('last_briefing_date', None) # Получаем дату, когда последний раз был проведен брифинг

    image_context = get_screenshot_context() # Получаем в контекст изображение экрана

    if last_briefing_date_str != today_date_str and current_hour >= general_settings.BRIEFING_START_HOUR: # Сравнивает текущую дату и дату в 'last_briefing_date': если даты разные - СЛЕДУЕТ ПРОВЕСТИ БРИФИНГ
        try:
            print("Generating a briefing.")
            from assistant_tools.skills import get_weather, get_habr_news
            from assistant_vector_database.database import vectorstore

            # Собираем данные для брифинга
            now = datetime.datetime.now()
            time_str = now.strftime("%H:%M")
            weather_data = get_weather() # Получаем погоду
            habr_news = get_habr_news(limit=general_settings.NUM_OF_NEWS_IN_BRIEFING) # Получаем свежие новости
            memory_database = vectorstore.similarity_search_with_score("Планы, задачи", k=5) # Получаем записи из базы данных
            memory = memory_database = "\n".join([record.page_content for record, score in memory_database]) # Сортируем в красивую строку, можно добавить if score <= general_settings.SIMILARITY_THRESHOLD если в базу данных попадается шелуха
            logger.debug(f"Записи в датабазе для утреннего брифинга: {memory}")

            initial_contents = [
            general_settings.VEGA_PERSONALITY_CORE + f"""
            Your task is to conduct a briefing for Sir. This is the first activation of the day (be prepared for activation at any time, whether it's 02:00 or 13:00).

            Analyze and synthesize the raw data provided below. Your report must be a single, coherent text, not a list of facts.

            Structure guidelines (use as inspiration):
            Begin with a greeting appropriate for the time of day/evening/whenever the user has activated you.
            Briefly mention key weather indicators. You may add a sarcastic comment if the weather is unfavorable.
            Select the 1-2 most important or interesting news items from the list and present them in a concise form. Do not list everything.
            Briefly mention the overall system status if there is anything noteworthy (e.g., high load).
            If the user has set any tasks for himself or anything else, you may, but are not obligated to, remind him of them in your own manner. Pay attention to dates in your memory and compare them with the current one, as this is quite important: records that are sufficiently old can be omitted.
            Conclude the briefing with a business-like, motivational, or sarcastic remark that summarizes the situation.

            Maintain your style: brevity, analytics, professionalism, and subtle sarcasm.

            Here is the raw data for analysis:
            Current time and date: {time_str}
            Current weather in Lipetsk: {weather_data};
            Current news from Habr: {habr_news};
            Data from your memory (you may skip this if it contains nothing useful): {memory}

            Here is the previous dialogue (may be useful for context):
            {short_term_memory}

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
            publish("GEMINI_RESPONSE", text=greeting_text)

            current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            short_term_memory.append(f"{current_date}, User activated the system.")
            short_term_memory.append(f"{current_date}, V.E.G.A. (briefing): {greeting_text}") # Запись в кратковременную память
            save_memory()

            tasks_completed_today['last_briefing_date'] = today_date_str # Меняем дату последнего брифинга на сегодня
            # tasks_completed_today['briefing_completed'] = True
            write_json(tasks_file, tasks_completed_today)

        except Exception as e:
            print(f"[Brain] Error when addressing Gemini API: {e}")
        
    else: # ЕСЛИ ЗАПУСК НЕ ПЕРВЫЙ ЗА ДЕНЬ ИЛИ ЧАС МЕНЬШЕ УСТАНОВЛЕННОГО - СТАНДАРТНОЕ ПРИВЕТСТВИЕ
        print("Generating a standard greeting protocol.")
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M")
        try:
            initial_contents = [
            general_settings.VEGA_PERSONALITY_CORE + f"""
            Here's the previous conversation (useful for context):
            {short_term_memory}

            The user just launched you again earlier today. The current time is: {time_str}.
            Your task is to greet the user. Your greeting should be as personalized as possible and include a witty or sarcastic comment.

            Keep the tone personal.
            Keep the tone brief, businesslike, and sarcastic, similar to Jarvis. Your name is feminine.
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
            publish("GEMINI_RESPONSE", text=greeting_text)

            current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            short_term_memory.append(f"{current_date}, User activated the system.")
            short_term_memory.append(f"{current_date}, V.E.G.A.: {greeting_text}") # Запись в кратковременную память
            save_memory()

        except Exception as e:
            print(f"[Brain] Error when addressing Gemini API: {e}")

def litany_of_analysis_screen():
    """По горячей клавише (по умолчанию - 'ctrl+alt+shift+a') вызывает Вегу и говорит ей, что нужно анализировать экран (для помощи в чем-то)."""
    print("A litany of screen analysis has been called.")
    img = get_screenshot_context()
    try:
        initial_contents = [
            general_settings.VEGA_PERSONALITY_CORE,
            f"""
            Current Directive: "What Now?"

            Sir has activated the hotkey protocol. Your primary function is to analyze the screen buffer to deduce the reason for this summons. The cause may range from a critical system fault, to a perplexing social entanglement, or simply existential laziness.

            Possible scenarios include:

            Chat Interface: Probably that Sir requires you to formulate a response on your behalf (as [V.E.G.A.]) and/or analyze the ongoing dialogue, profile the other participant. 
            In most cases, a chat consists of a user and their interlocutor. In this case, you can take on a kind of "third party" role.

            Meme/Humor Artifact: It is possible the user is requesting an evaluation of a joke or an internet meme... The motives for such a request are currently outside standard operating parameters.
            Code/IDE: Likely a logical deadlock or a runtime error. Your task is to identify the fault.
            Webpage/Document: He likely requires an assessment of the text and a summary (in that case, you can make it a little longer to show more information).
            Unfamiliar Application/System Prompt: The user has encountered an unknown interface or system message. Your directive is to provide assistance.

            A quick reminder: If, for example, a user is reading an article, you shouldn't start your response by saying "Sir, you are reading..." - you should get straight to the point.

            
            Here is the preceding dialogue log (it may provide context):

            {short_term_memory}

            """
        ]
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
        print(f"V.E.G.A.: {final_text_to_publish}")
        publish("GEMINI_RESPONSE", text=final_text_to_publish)
        _process_interaction("The user clicked the screen analysis button", final_text_to_publish)

    except Exception as e:
        print(f"Error when addressing Gemini API: {e}")




