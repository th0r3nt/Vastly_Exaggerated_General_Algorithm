# music_skills.py
import subprocess
import os
import random
from fuzzywuzzy import process
import logging
from assistant_general.logger_config import setup_logger
from dotenv import load_dotenv

load_dotenv()
setup_logger()
logger = logging.getLogger(__name__)

FOOBAR_PATH = os.getenv("FOOBAR_PATH")
MUSIC_LIBRARY_PATH = os.getenv("MUSIC_LIBRARY_PATH")
SILENT_TRACK_PATH = os.getenv("SILENT_TRACK_PATH")

# ЧТОБЫ СОЗДАВАЛСЯ НОВЫЙ ПЛЕЙЛИСТ В КОДЕ, НАДО:
# НАПИСАТЬ СНАЧАЛА success = _send_foobar_command(['/add', random_track_path]), А УЖЕ ПОТОМ
# success = _send_foobar_command(['/play', playlist_path])
# ТАК КАК ЕСТЬ НАПИСАТЬ success = _send_foobar_command(['/add', random_track_path '/play',]) ВМЕСТЕ,
# ПЛЕЙЛИСТ НЕ СОЗДАСТСЯ

setup_logger()
logger = logging.getLogger(__name__)


def _send_foobar_command(command_args):
    """Системная команда для других функций, управляет Foobar2000."""
    try:
        full_command = [FOOBAR_PATH] + command_args
        subprocess.Popen(full_command)
        return True
    except FileNotFoundError:
        logger.error("File not found.")
        return False
    except Exception as e:
        print(f"ERROR while executing Foobar2000 command: {e}")
        return False

def _current_tracks():
    """Проходит по всем файлам в музыкальной библиотеке и возвращает список путей ко всем трекам."""
    all_tracks_list = []

    for root, dirs, files in os.walk(MUSIC_LIBRARY_PATH): # Рекурсивно обходим всю музыкальную библиотеку
        for filename in files: # Проходимся по файлам

            full_path = os.path.join(root, filename)
            
            # Добавляем найденный полный путь в наш список
            all_tracks_list.append(full_path)
    return all_tracks_list

ALL_TRACKS_CACHE = _current_tracks() # Получает все файлы из музыкальной библиотеки и пути к ним

def _find_best_track_path(query: str, all_tracks_paths: list, score_cutoff=80):
    """Ищет наиболее похожее название трека в кеше и возвращает ПОЛНЫЙ ПУТЬ."""
    track_map = {os.path.splitext(os.path.basename(path))[0]: path for path in all_tracks_paths}
    best_match = process.extractOne(query, track_map.keys())
    if best_match and best_match[1] >= score_cutoff:
        return track_map[best_match[0]]
    return None

def music_play_track(track_name: str = None, artist_name: str = None):
    """Ищет наиболее похожий трек и воспроизводит его."""
    if not track_name and not artist_name:
        return "Must be specify the track title or artist name."

    # Собираем единый поисковый запрос
    search_query = f"{artist_name or ''} {track_name or ''}".strip()
    
    found_path = _find_best_track_path(search_query, ALL_TRACKS_CACHE)

    if found_path:
        _send_foobar_command(['/add', found_path])
        _send_foobar_command(['/play', found_path])
        clean_name = os.path.splitext(os.path.basename(found_path))[0]
        return f"Play: {clean_name}"
    else:
        return f"Track similar to '{search_query}' not found in the library."
    
def music_play_playlist(playlist_name: str):
    """Ищет папку по имени, очищает старый плейлист, добавляет все треки из папки и начинает играть."""
    if not playlist_name:
        return "Must specify a playlist name."

    playlist_path = None
    try:
        with os.scandir(MUSIC_LIBRARY_PATH) as entries:
            for entry in entries:
                if entry.is_dir() and playlist_name.lower() in entry.name.lower():
                    playlist_path = entry.path
                    print(f"Playlist found: {playlist_path}")
                    break
    except FileNotFoundError:
        logger.error("Error: Music library folder not found.")
        return "Error: Music library folder not found."

    if playlist_path:
        try:
            track_count = sum(1 for f in os.listdir(playlist_path) if f.lower().endswith(('.mp3', '.flac', '.wav', '.ogg', '.m4a')))
            if track_count == 0:
                return f"Плейлист '{playlist_name}' найден, но он пуст."
        except Exception as e:
            logger.error(f"Не удалось прочитать содержимое плейлиста '{playlist_name}': {e}")
            return f"Не удалось прочитать содержимое плейлиста '{playlist_name}': {e}"

        success = _send_foobar_command(['/add', playlist_path])
        success = _send_foobar_command(['/play', playlist_path])
        
        if success:
            return f"Включаю плейлист '{playlist_name}'. Найдено треков: {track_count}."
        else:
            return "Не удалось запустить воспроизведение плейлиста."
    else:
        return f"Плейлист '{playlist_name}' не найден."
    
def music_play_random():
    """Выбирает случайный трек из всей музыкальной библиотеки и включает его."""
    if not ALL_TRACKS_CACHE:
        return "Music library is empty. There's nothing to play."
        
    # Выбираем случайный полный путь к файлу из кеша
    random_track_path = random.choice(ALL_TRACKS_CACHE)
    
    clean_name = os.path.splitext(os.path.basename(random_track_path))[0]

    success = _send_foobar_command(['/add', random_track_path])
    success = _send_foobar_command(['/play', random_track_path])
    
    if success:
        return f"Random track played: {clean_name}"
    else:
        return "Failed to start playing random track."

def music_play_random_album():
    """Находит все папки (альбомы/плейлисты) в музыкальной библиотеке, выбирает одну случайную и воспроизводит её."""
    try:
        # Получаем список всех записей в директории и фильтруем, оставляя только папки
        all_playlists = [entry.path for entry in os.scandir(MUSIC_LIBRARY_PATH) if entry.is_dir()]
    except FileNotFoundError:
        logger.error("Error: Music library folder not found.")
        return "Error: Music library folder not found."

    if not all_playlists:
        logger.info("No ready-made playlists (folders) were found in the music library.")
        return "No ready-made playlists (folders) were found in the music library."

    random_playlist_path = random.choice(all_playlists) # Выбираем случайный путь к плейлисту из списка
    playlist_name = os.path.basename(random_playlist_path) # Получаем чистое имя для красивого ответа
    
    _send_foobar_command(['/add', random_playlist_path])
    success = _send_foobar_command(['/play', random_playlist_path])
    
    if success:
        logger.debug(f"Random playlist enabled: '{playlist_name}'.")
        return f"Random playlist enabled: '{playlist_name}'."
    else:
        logger.error("Failed to start playing random playlist.")
        return "Failed to start playing random playlist."

def music_pause_playback():
    """Ставит текущий трек на паузу."""
    success = _send_foobar_command(['/pause'])
    return "Playback is paused." if success else "Failed to pause."

def music_resume_playback():
    """Снимает воспроизведение с паузы."""
    success = _send_foobar_command(['/play'])
    return "Playback resumed." if success else "Failed to resume."

def music_play_next_track():
    """Включает следующий трек в плейлисте."""
    success = _send_foobar_command(['/next'])
    return "Next track is on." if success else "Failed to change track."

def music_play_previous_track():
    """Включает предыдущий трек в плейлисте."""
    success = _send_foobar_command(['/prev'])
    return "Previous track is on." if success else "Failed to change track."

def music_clear_playlist():
    """Очищает текущий плейлист, заменяя его одним треком с тишиной и останавливая воспроизведение. 
    Единственный надежный способ эмулировать команду 'clear'."""

    # Проверка, что наш инструмент на месте
    if not os.path.exists(SILENT_TRACK_PATH):
        msg = f"ERROR: Cleanup file '{SILENT_TRACK_PATH}' not found."
        print(msg)
        return msg
        
    # Главная команда: Остановить -> Заменить плейлист на "пустышку"
    success = _send_foobar_command(['/add', SILENT_TRACK_PATH])
    success = _send_foobar_command(['/play', SILENT_TRACK_PATH])
    
    if success:
        return "Playlist cleared."
    else:
        return "Failed to clear playlist."


if __name__ == "__main__":
    # Тесты
    import time
    music_play_track("horizon")
    time.sleep(7)
    music_play_track("мозговой протез")
    time.sleep(7)
    music_play_playlist("slipknot")
    time.sleep(7)
    music_play_next_track()
    music_play_next_track()
    time.sleep(7)
    music_pause_playback()
