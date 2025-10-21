# systemic_skills.py
import json
from assistant_tools.utils import play_sfx

def read_json(filename: str):
    """Читает JSON-файл. Если файла нет или он поврежден, создает его с содержимым по умолчанию и возвращает его."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Если файла нет или он пустой/битый
        print(f"Файл '{filename}' не найден или поврежден.")
        play_sfx("error")
        return {
            "last_briefing_date": "1970-01-01"
        }
    
def write_json(filename: str, data: dict):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        play_sfx("error")
        return f"Error writing to json file: {e}"