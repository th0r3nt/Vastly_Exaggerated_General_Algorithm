from api_keys import OPENWEATHER_API_KEY, WEATHER_CITY_LAT, WEATHER_CITY_LON
import webbrowser
import requests


def get_weather(city_name: str):
    """Получает текущую погоду"""
    if city_name:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
    else: # Если город не передан, узнаем в Липецке
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={WEATHER_CITY_LAT}&lon={WEATHER_CITY_LON}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"

    response = requests.get(url)
    weather_data = response.json()
    weather_description = weather_data["weather"][0]["description"] # Например, "пасмурно"
    description_of_feeling_temp = weather_data["main"]["feels_like"]
    description_of_temp = weather_data["main"]["temp"]
    humidity = weather_data["main"]["humidity"] # Влажность, например, 36
    wind = weather_data["wind"]["speed"] # Скорость ветра, например, 4.64
    sity_name = weather_data["name"]

    final_answer = f"Город: {sity_name}; \n Описание погоды - {weather_description}; \n Ощущается как - {description_of_feeling_temp} градусов; \n Реальная температура - {description_of_temp} градусов; \n Влажность воздуха - {humidity}; \n Ветер - {wind} м/с"
    print(final_answer)
    return final_answer





get_weather("Москва")