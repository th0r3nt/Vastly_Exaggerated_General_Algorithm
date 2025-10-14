# import os
# from fuzzywuzzy import process

# MUSIC_LIBRARY_PATH = "C:\\Users\\ivanc\\Desktop\\Project_V.E.G.A\\VEGA_core\\assistant_music\\music"

# def find_best_match(song_query: str):
#     """Проходит по всем файлам, находит лучшее совпадение и возвращает его."""
    
#     all_tracks_names = []
    
#     # ПРАВИЛЬНЫЙ СПОСОБ использования os.walk
#     for root, dirs, files in os.walk(MUSIC_LIBRARY_PATH): # В os.walk: root — путь к текущей папке; dirs — список названий подпапок в этой папке; files — список названий файлов в этой папке
#         for filename in files:
            
#             clean_name = os.path.splitext(filename)[0]
#             all_tracks_names.append(clean_name)

#     print("--- Список для поиска ---")
#     print(all_tracks_names)
#     print("\n")

#     best_match = process.extractOne(song_query, all_tracks_names)
#     print(f"Результат поиска: {best_match}")
#     return best_match

# while True:
#     song = input("Введите песню для поиска: ")
#     if not song:
#         break
#     find_best_match(song)






import requests

try:
    print("Пытаюсь подключиться к Google...")
    response = requests.get('https://www.google.com', timeout=10)
    print(f"Успех! Статус-код: {response.status_code}")
    print("Значит, базовый выход в интернет из Python работает.")
except Exception as e:
    print("\nПИЗДЕЦ! Опять ошибка!")
    print(f"Не удалось подключиться. Ошибка: {e}")