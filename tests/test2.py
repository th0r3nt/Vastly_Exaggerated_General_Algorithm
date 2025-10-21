import os
from dotenv import load_dotenv

load_dotenv()

MUSIC_LIBRARY_PATH = os.getenv("MUSIC_LIBRARY_PATH")

def all_names_playlists():
    """Возвращает названия всех существующих плейлистов"""
    all_names_playlists = [playlist.name for playlist in os.scandir(MUSIC_LIBRARY_PATH)]
    all_names = "; ".join(all_names_playlists)
    return all_names

print(all_names_playlists())