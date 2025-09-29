# skills.py
import webbrowser
import requests
import datetime
import pyautogui  
import os
from dotenv import load_dotenv
from assistant_vector_database.database import add_new_memory

load_dotenv() # для загрузки API ключей из .env
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHER_CITY_LAT = os.getenv("WEATHER_CITY_LAT")
WEATHER_CITY_LON = os.getenv("WEATHER_CITY_LON")

MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")

def get_weather(city_name: str):
    """Получает текущую погоду"""
    if city_name:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
    else: # Если город не передан, узнаем в Липецке
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={WEATHER_CITY_LAT}&lon={WEATHER_CITY_LON}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"

    response = requests.get(url)
    weather_data = response.json()
    weather_description = weather_data["weather"][0]["description"] # Например, "пасмурно"
    description_of_feeling_temp = int(weather_data["main"]["feels_like"])
    description_of_temp = int(weather_data["main"]["temp"])
    humidity = int(weather_data["main"]["humidity"]) # Влажность, например, 36

    wind = weather_data["wind"]["speed"] # Скорость ветра, например, 4.64
    sity_name = weather_data["name"]

    final_answer = f"City: {sity_name}; \nWeather description: {weather_description}; \nFeels like: {description_of_feeling_temp}°; \n Actual temperature: {description_of_temp}°; \n Air humidity: {humidity}; \n Wind: {wind} m/s."
    print(final_answer)
    return final_answer

def search_in_google(search_query: str) -> str:
    """Ищет переданный запрос в поисковике и открывает вкладку браузера."""
    if not search_query:
        return "Error: A search query is required to search."
    webbrowser.open(f"https://yandex.ru/search/?text={search_query}") #Альтернативно https://www.google.com/search?q=
    return f"The search page for the query is open: '{search_query}'."

def get_time(**kwargs) -> str:
    """Возвращает текущее время в формате ЧЧ:ММ."""
    now = datetime.datetime.now()
    return f"Current time: {now.strftime('%H:%M')}."

def get_date() -> str:
    """Возвращает сегодняшнюю дату."""
    now = datetime.datetime.now()
    return f"Today {now.day} {MONTHS[now.month - 1]}."

def make_screenshot():
    filename = "screenshot.png"
    try:
        screenshot = pyautogui.screenshot(filename)  
        screenshot.save(filename)  
        return {"status": "success", "file_path": os.path.abspath(filename)}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
def save_to_memory(text):
    """Сохраняет в память любой факт о пользователе"""
    add_new_memory(text)
