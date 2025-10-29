# music_skills.py
import subprocess
import os
import random
from fuzzywuzzy import process
import logging
# from assistant_general.logger_config import setup_logger
from dotenv import load_dotenv
from assistant_tools.utils import play_sfx

load_dotenv()
# setup_logger()
logger = logging.getLogger(__name__)

FOOBAR_PATH = os.getenv("FOOBAR_PATH")
MUSIC_LIBRARY_PATH = os.getenv("MUSIC_LIBRARY_PATH")
SILENT_TRACK_PATH = os.getenv("SILENT_TRACK_PATH")

# ДЛЯ РЕГИСТРАЦИИ НОВЫХ НАВЫКОВ В ВЕГУ НУЖНО:
# Написать json схему в music_skills_diagrams.py
# Перейти в assistant_brain.added_skills.py и следовать инструкциям, которые описаны в файле

# ЧТОБЫ СОЗДАВАЛСЯ НОВЫЙ ПЛЕЙЛИСТ В КОДЕ, НАДО:
# НАПИСАТЬ СНАЧАЛА success = _send_foobar_command(['/add', random_track_path]), А УЖЕ ПОТОМ
# success = _send_foobar_command(['/play', playlist_path])
# ТАК КАК ЕСЛИ НАПИСАТЬ success = _send_foobar_command(['/add', random_track_path '/play',]) ВМЕСТЕ,
# ПЛЕЙЛИСТ НЕ СОЗДАСТСЯ

# setup_logger()
logger = logging.getLogger(__name__)

def _send_foobar_command(command_args):
    """Системная команда для других функций, управляет Foobar2000."""
    try:
        full_command = [FOOBAR_PATH] + command_args
        subprocess.Popen(full_command)
        return True
    except FileNotFoundError:
        logger.error("File not found.")
        play_sfx('silent_error')
        return False
    except Exception as e:
        logger.error(f"Error while executing Foobar2000 command: {e}")
        play_sfx('silent_error')
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
    play_sfx('silent_execution')
    if not track_name and not artist_name:
        play_sfx('silent_error')
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
        play_sfx('silent_error')
        return f"Track similar to '{search_query}' not found in the library."
    
def music_play_playlist(playlist_name: str):
    """Ищет папку по имени, очищает старый плейлист, добавляет все треки из папки и начинает играть."""
    play_sfx('silent_execution')
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
        play_sfx('silent_error')
        return "Error: Music library folder not found."

    if playlist_path:
        try:
            track_count = sum(1 for f in os.listdir(playlist_path) if f.lower().endswith(('.mp3', '.flac', '.wav', '.ogg', '.m4a')))
            if track_count == 0:
                return f"Playlist '{playlist_name}' was found, but it is empty."
        except Exception as e:
            logger.error(f"Failed to read contents of playlist '{playlist_name}': {e}")
            play_sfx('silent_error')
            return f"Failed to read contents of playlist '{playlist_name}': {e}"

        success = _send_foobar_command(['/add', playlist_path])
        success = _send_foobar_command(['/play', playlist_path])
        
        if success:
            logger.info(f"Playlist '{playlist_name}' is enabled. Tracks found: {track_count}.")
            return f"Playlist '{playlist_name}' is enabled. Tracks found: {track_count}."
        else:
            logger.error("Failed to start playing the playlist.")
            play_sfx('silent_error')
            return "Failed to start playing the playlist."
    else:
        logger.error(f"Playlist '{playlist_name}' not found.")
        play_sfx('silent_error')
        return f"Playlist '{playlist_name}' not found."

def music_pause_playback():
    """Ставит текущий трек на паузу."""
    play_sfx('silent_execution')
    success = _send_foobar_command(['/pause'])
    return "Playback is paused." if success else "Failed to pause."

def music_resume_playback():
    """Снимает воспроизведение с паузы."""
    play_sfx('silent_execution')
    success = _send_foobar_command(['/play'])
    return "Playback resumed." if success else "Failed to resume."

def music_play_next_track():
    """Включает следующий трек в плейлисте."""
    play_sfx('silent_execution')
    success = _send_foobar_command(['/next'])
    return "Next track is on." if success else "Failed to change track."

def music_play_previous_track():
    """Включает предыдущий трек в плейлисте."""
    play_sfx('silent_execution')
    success = _send_foobar_command(['/prev'])
    return "Previous track is on." if success else "Failed to change track."

def music_clear_playlist():
    """Очищает текущий плейлист, заменяя его одним треком с тишиной и останавливая воспроизведение. 
    Единственный надежный способ эмулировать команду 'clear'."""
    play_sfx('silent_execution')

    # Проверка, что наш инструмент на месте
    if not os.path.exists(SILENT_TRACK_PATH):
        msg = f"Cleanup file '{SILENT_TRACK_PATH}' not found."
        logger.error(msg)
        return msg
        
    # Главная команда: Остановить -> Заменить плейлист на "пустышку"
    success = _send_foobar_command(['/add', SILENT_TRACK_PATH])
    success = _send_foobar_command(['/play', SILENT_TRACK_PATH])
    
    if success:
        return "Playlist cleared."
    else:
        play_sfx('silent_error')
        return "Failed to clear playlist."
    
def all_names_playlists():
    """Возвращает названия всех папок-плейлистов в музыкальной библиотеке."""
    try:
        playlist_names = [entry.name for entry in os.scandir(MUSIC_LIBRARY_PATH) if entry.is_dir()]
        if playlist_names:
            playlists = "Available playlists: \n" + "; \n".join(playlist_names)
            print(playlists)
            return playlists
        else:
            logger.info("No playlists found in the music library.")
            play_sfx('silent_error')
            return "No playlists found in the music library."
    except Exception as e:
        logger.error(f"Error reading playlist list: {e}")
        play_sfx('silent_error')
        return f"Error reading playlist list: {e}"
    
def all_tracks_in_playlist(playlist_name: str):
    """Возвращает названия всех треков в указанном плейлисте."""
    play_sfx('silent_execution')
    playlist_path = os.path.join(MUSIC_LIBRARY_PATH, playlist_name)
    if not os.path.isdir(playlist_path):
        logger.info("Плейлист '{playlist_name}' не найден.")
        return f"Плейлист '{playlist_name}' не найден."
    try:
        track_names = [os.path.splitext(f.name)[0] for f in os.scandir(playlist_path) if f.is_file()]
        if track_names:
            all_tracks = f"Треки в плейлисте '{playlist_name}': " + "; \n".join(track_names)
            print(all_tracks)
            return all_tracks
        else:
            logger.info(f"Плейлист '{playlist_name}' пуст.")
            play_sfx('silent_error')
            return f"Плейлист '{playlist_name}' пуст."
    except Exception as e:
        logger.error(f"Ошибка при чтении треков из плейлиста: {e}")
        play_sfx('silent_error')
        return f"Ошибка при чтении треков из плейлиста: {e}"


if __name__ == "__main__":
    # Тесты
    import time
    music_play_playlist("slipknot")
    time.sleep(7)
