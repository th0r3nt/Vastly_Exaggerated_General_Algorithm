# brain.py
import google.generativeai as genai
from google import genai  # noqa: F811
from google.genai import types
import threading
import os
import json
import datetime
from collections import deque
from dotenv import load_dotenv
from assistant_event_bus.event_bus import subscribe, publish
from assistant_tools.utils import play_sfx
import assistant_general.general_settings as general_settings
from added_skills import function_declarations, skills_registry # ДОБАВЛЯТЬ НОВЫЕ УМЕНИЯ В ЭТОТ ФАЙЛ

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

def process_interaction(query, final_text_to_publish):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    short_term_memory.append(f"{current_date}, User: {query}")
    short_term_memory.append(f"{current_date}, V.E.G.A.: {final_text_to_publish}")
    save_memory() # Важно: Сохранять нужно либо после каждого добавления, либо при завершении программы

def run_gemini_task(**kwargs):
    query = kwargs.get('query')
    database_context = kwargs.get('database_context')
    try:
        response = client.models.generate_content(
        model=general_settings.MODEL_GEMINI,
        contents=general_settings.VEGA_PERSONALITY_CORE + 

        f"""Right now, your task is to maintain a conversation. 
        Don't deviate from your personality. BE BRIEF! Your name is feminine.

        Here's the relevant information from your database (memory). Use it to provide the most complete answer. If the information is irrelevant, you can ignore it.
        {database_context}


        Here's the previous dialogue (useful for context):
        {short_term_memory}


        User request: {query}
        V.E.G.A: 
        """,
        config=config,
        )

        function_call_found = False
        results_of_tool_calls = [] # Полезно, если нужно несколько вызовов Function Calling

        # Проверяем наличие вызовов Function Calling
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call') and part.function_call is not None:
                function_call = part.function_call

                print(f"\nFunction to call: {function_call.name}")
                print(f"Arguments: {function_call.args}\n")

                function_call_found = True

                function_to_call = skills_registry[function_call.name]
                result = function_to_call(**function_call.args) # result = например, результат вызова skills.get_weather(city_name="Липецк")"; ** распоковывает словарь в именованные аргументы

                history = response.candidates[0].content

                function_response_part = types.Part(
                    function_response=types.FunctionResponse(
                        name=function_call.name,    # Говорим, какую функцию вызвали
                        response={'result': result} # Передаем результат, лучше обернуть в словарь
                    )
                )

                results_of_tool_calls.append(function_response_part)

        if function_call_found:
            final_response = client.models.generate_content(
                model=general_settings.MODEL_GEMINI,
                contents=[general_settings.VEGA_PERSONALITY_CORE, history, *results_of_tool_calls], # оператор распоковки списка - args звездочка нужна, чтобы не было списка внутри списка (по типу [ <ответ про погоду>, <ответ про дату> ])
                config=config,
            )

            final_text_to_publish = final_response.text

        if not function_call_found:
            final_text_to_publish = response.text

        print(f"V.E.G.A.: {final_text_to_publish}")
        publish("GEMINI_RESPONSE", text=final_text_to_publish)
        process_interaction(query, final_text_to_publish) # Сохранение в кратковременную память

    except ConnectionError as e:
        print(f"Error when addressing Gemini API: {e}")

def generate_response(*args, **kwargs):
    """Принимает данные от поисковика и запускает генерацию ответа в отдельном потоке."""
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

    worker_thread = threading.Thread(
        target=run_gemini_task, 
        kwargs={"query": query, "database_context": database_context}
    )
    worker_thread.start()

    print("\n[Brain] The task for Gemini has been sent to the background.")

def initialize_brain():
    subscribe("USER_SPEECH_AND_RECORDS_FOUND_IN_DB", generate_response)

def generate_greetings():
    now = datetime.datetime.now()
    time_str = now.strftime("%H:%M")

    try:
        response = client.models.generate_content(
        model=general_settings.MODEL_GEMINI,
        contents=general_settings.VEGA_PERSONALITY_CORE + f"""
        Here's the previous dialogue (useful for context):
        {short_term_memory}

        

        The user has launched you. The current time is: {time_str}.
        Your task is to greet the user. Your greeting SHOULD be as personalized as possible and include a witty or sarcastic comment on any issue: 
        whether it's the frequency of data posting, for example, if the last post was very recent (less than 5 minutes), or an unusual time. 
        Alternatively, you can use context from previous conversations. If such a sarcastic comment doesn't work, greet the user normally. 
        Keep the tone brief, businesslike, and sarcastic, similar to Jarvis. Your name is feminine.
        """,
        config=config,
        )

        play_sfx("system_startup")
        print(f"V.E.G.A.: {response.text}")
        publish("GEMINI_RESPONSE", text=response.text)

        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        short_term_memory.append(f"{current_date}, User activated the system.")
        short_term_memory.append(f"{current_date}, V.E.G.A.: {response.text}") # Запись в кратковременную память
        save_memory()

    except Exception as e:
        print(f"[Brain] Error when addressing Gemini API: {e}")



