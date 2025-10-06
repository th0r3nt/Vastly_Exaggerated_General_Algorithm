# music_skills.py
import subprocess
import os
import random
from assistant_general.general_settings import FOOBAR_PATH, MUSIC_LIBRARY_PATH, SILENT_TRACK_PATH

# ЧТОБЫ СОЗДАВАЛСЯ НОВЫЙ ПЛЕЙЛИСТ В КОДЕ, НАДО:
# НАПИСАТЬ СНАЧАЛА success = _send_foobar_command(['/add', random_track_path]), А УЖЕ ПОТОМ
# success = _send_foobar_command(['/play', playlist_path])
# ТАК КАК ЕСТЬ НАПИСАТЬ success = _send_foobar_command(['/add', random_track_path '/play',]) ВМЕСТЕ,
# ПЛЕЙЛИСТ НЕ СОЗДАСТСЯ

def _send_foobar_command(command_args):
    """Системная команда для других функций, управляет Foobar2000."""
    try:
        full_command = [FOOBAR_PATH] + command_args
        subprocess.Popen(full_command)
        return True
    except FileNotFoundError:
        print(f"ОШИБКА: foobar2000.exe не найден по пути: {FOOBAR_PATH}")
        return False
    except Exception as e:
        print(f"ОШИБКА при выполнении команды Foobar2000: {e}")
        return False

def _current_tracks():
    """Проходит по всем файлам в музыкальной библиотеке и возвращает список путей ко всем трекам."""
    all_tracks_list = []

    for root, dirs, files in os.walk(MUSIC_LIBRARY_PATH): # Рекурсивно обходим всю музыкальную библиотеку
        for filename in files: # Проходимся по файлам
            if not filename.lower().endswith(('.mp3', '.flac', '.wav', '.ogg', '.m4a')):
                continue

            full_path = os.path.join(root, filename)
            
            # Добавляем найденный полный путь в наш список
            all_tracks_list.append(full_path)
    return all_tracks_list

ALL_TRACKS_CACHE = _current_tracks() # Получает все файлы из музыкальной библиотеки и пути к ним

def music_play_track(track_name: str = None, artist_name: str = None):
    """Ищет трек и немедленно начинает его воспроизведение, удаляя текущий плейлист и создавая новый."""
    if not track_name and not artist_name:
        return "You must specify the name of the track and/or artist."

    print(f"Searching for track: [Artist: {artist_name or 'Any'}, Title: {track_name or 'Any'}]")
    found_path = None
    
    for root, dirs, files in os.walk(MUSIC_LIBRARY_PATH):
        for filename in files:
            full_path = os.path.join(root, filename)
            
            artist_match = True
            track_match = True

            if artist_name and artist_name.lower() not in full_path.lower():
                artist_match = False
            
            if track_name and track_name.lower() not in filename.lower():
                track_match = False
            
            if artist_match and track_match:
                found_path = full_path
                break
        
        if found_path:
            break

    if found_path:
        print(f"Track is found: {found_path}")

        success_add = _send_foobar_command(['/add', found_path])
        if success_add:
            success_play = _send_foobar_command(['/play', found_path])
            if success_play:
                clean_name = os.path.splitext(os.path.basename(found_path))[0]
                return f"Play: {clean_name}"
        
        return "Unable to start playback in Foobar2000."
    else:
        print("Track not found in the entire library.")
        return "Track not found in library."
    
def music_play_playlist(playlist_name: str):
    """Ищет папку по имени, очищает старый плейлист, добавляет все треки из папки и начинает играть."""
    if not playlist_name:
        return "Необходимо указать название плейлиста."

    playlist_path = None
    try:
        with os.scandir(MUSIC_LIBRARY_PATH) as entries:
            for entry in entries:
                if entry.is_dir() and playlist_name.lower() in entry.name.lower():
                    playlist_path = entry.path
                    print(f"Playlist found: {playlist_path}")
                    break
    except FileNotFoundError:
        return "Error: Music library folder not found."

    if playlist_path:
        try:
            track_count = sum(1 for f in os.listdir(playlist_path) if f.lower().endswith(('.mp3', '.flac', '.wav', '.ogg', '.m4a')))
            if track_count == 0:
                return f"Плейлист '{playlist_name}' найден, но он пуст."
        except Exception as e:
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
        return f"Random track included: {clean_name}"
    else:
        return "Failed to start playing random track."

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
    """
    Очищает текущий плейлист, заменяя его одним треком с тишиной и останавливая воспроизведение.
    Единственный надежный способ эмулировать команду 'clear'.
    """

    # Проверка, что наш инструмент на месте
    if not os.path.exists(SILENT_TRACK_PATH):
        msg = f"ERROR: Cleanup file '{SILENT_TRACK_PATH}' not found."
        print(msg)
        return msg
        
    # Главная команда: Остановить -> Заменить плейлист на "пустышку"
    success = _send_foobar_command(['/add', SILENT_TRACK_PATH])
    success = _send_foobar_command(['/play', SILENT_TRACK_PATH])
    
    if success:
        # Можно даже удалить этот трек из плейлиста, если он мешает
        # Но это усложнение, для начала хватит и так.
        return "Playlist cleared."
    else:
        return "Failed to clear playlist."
