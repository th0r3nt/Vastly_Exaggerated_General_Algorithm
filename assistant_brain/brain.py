# brain.py
import google.generativeai as genai
from assistant_event_bus.event_bus import subscribe, publish
import threading
from assistant_general.config import VEGA_PERSONALITY_CORE
from assistant_tools.skills_diagrams import get_weather_scheme, search_in_google_scheme, get_date_scheme, get_time_scheme, make_screenshot_scheme # 1. Импорт схемы нового инструмента
from google import genai  # noqa: F811
from google.genai import types
import assistant_tools.skills
from assistant_tools.utils import play_sfx
import os
from dotenv import load_dotenv

load_dotenv() # для загрузки API ключей из .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
tools = types.Tool(function_declarations=[get_weather_scheme, search_in_google_scheme, get_date_scheme, get_time_scheme, make_screenshot_scheme]) # 2. Регистрация json-схемы нового инструмента
config = types.GenerateContentConfig(tools=[tools])

skills_registry = {"get_weather": assistant_tools.skills.get_weather,
                   "search_in_google": assistant_tools.skills.search_in_google,
                   "get_date": assistant_tools.skills.get_date,
                   "get_time": assistant_tools.skills.get_time,
                   "make_screenshot": assistant_tools.skills.make_screenshot} # 3. Указание, какой навык использовать

def run_gemini_task(**kwargs):
    text = kwargs.get('text')
    try:
        response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents= VEGA_PERSONALITY_CORE + f"Right now, your task is to maintain a conversation. Don't deviate from your personality. \n\nUser request: {text}",
        config=config,
        )

        function_call_found = False
        results_of_tool_calls = []


        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call') and part.function_call is not None:
                function_call = part.function_call

                print(f"Function to call: {function_call.name}")
                print(f"Arguments: {function_call.args}")

                function_call_found = True

                function_to_call = skills_registry[function_call.name]
                result = function_to_call(**function_call.args) # result = например, результат вызова skills.get_weather(city_name="Липецк")", ** распоковывает словарь в именованные аргументы

                history = response.candidates[0].content

                function_response_part = types.Part(
                    function_response=types.FunctionResponse(
                        name=function_call.name,    # Говорим, какую функцию вызвали
                        response={'result': result} # Передаем результат. Лучше обернуть в словарь.
                    )
                )

                results_of_tool_calls.append(function_response_part)



        if function_call_found:
            final_response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=[VEGA_PERSONALITY_CORE, history, *results_of_tool_calls], # оператор распоковки списка - args звездочка нужна, чтобы не было списка внутри списка (по типу [ <ответ про погоду>, <ответ про дату> ])
                config=config,
            )

            final_text_to_publish = final_response.text


        if not function_call_found:
            final_text_to_publish = response.text

        print(f"V.E.G.A.: {final_text_to_publish}")
        publish("GEMINI_RESPONSE", text=final_text_to_publish)

    except Exception as e:
        print(f"[Brain] Error when addressing Gemini API: {e}")

def generate_response(*args, **kwargs):
    """Если появится событие USER_SPEECH - generate_response создаст отдельный поток размышлений мозга Gemini, чтобы не блокировать SpeechListener"""
    text = kwargs.get('text')
    if not text:
        return

    worker_thread = threading.Thread(target=run_gemini_task, kwargs={"text": text,}) # Создаем, собственно, отдельный поток
    worker_thread.start()

    print("\n[Brain] The task for Gemini has been sent to the background.")

def initialize_brain():
    subscribe("USER_SPEECH", generate_response)


def generate_greetings():
    try:
        response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents= VEGA_PERSONALITY_CORE + "Right now, your task is to greet the user. They've launched you. Greet them in your style.",
        config=config,
        )

        play_sfx("system_startup")
        print(f"V.E.G.A.: {response.text}")
        publish("GEMINI_RESPONSE", text=response.text)


    except Exception as e:
        print(f"[Brain] Error when addressing Gemini API: {e}")



