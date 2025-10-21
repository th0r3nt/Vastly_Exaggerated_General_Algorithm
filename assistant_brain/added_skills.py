# added_skills.py

# 1. ИМПОРТ СХЕМЫ НОВОГО ИНСТРУМЕНТА
from assistant_tools.skills_diagrams import ( # Базовые навыки
    get_weather_scheme, search_in_google_scheme, get_date_scheme, get_time_scheme, make_screenshot_scheme, save_to_memory_scheme, lock_pc_scheme,
    get_windows_layout_scheme, move_mouse_scheme, current_mouse_coordinates_scheme, click_mouse_scheme, scroll_mouse_scheme, drag_mouse_scheme,
    press_hotkey_scheme, copy_to_clipboard_scheme, write_text_scheme, system_command_scheme, get_processes_scheme, currently_open_windows_scheme,
    get_system_volume_scheme, set_system_volume_scheme, decrease_volume_scheme,
    increase_volume_scheme, get_habr_news_scheme, get_system_metrics_scheme,
)
from assistant_tools.music_skills_diagrams import ( # Отдельные музыкальные навыки
    music_play_random_scheme, music_pause_playback_scheme, music_resume_playback_scheme, music_play_next_track_scheme,
    music_play_previous_track_scheme, music_clear_playlist_scheme, music_play_playlist_scheme, music_play_track_scheme,
    music_play_random_album_scheme, all_names_playlists_scheme, all_tracks_in_playlist_scheme
)

from assistant_tools.socialmedia_skills_diagrams import ( # Навыки для соцсетей
    get_telegram_channel_info_scheme,
)

import assistant_tools.skills
import assistant_tools.music_skills
import assistant_tools.socialmedia_skills

# 2. РЕГИСТРАЦИЯ JSON-СХЕМЫ НОВОГО ИНСТРУМЕНТА ДЛЯ FUNCTION CALLING НЕЙРОСЕТИ (Чтобы нейросеть читала описание навыков и могла понимать, что и с какими параметрами вызывать навыки)
function_declarations = [
    # БАЗОВЫЕ НАВЫКИ
    get_weather_scheme, 
    search_in_google_scheme, 
    get_date_scheme, 
    get_time_scheme, 
    make_screenshot_scheme, 
    save_to_memory_scheme, 
    lock_pc_scheme,
    get_habr_news_scheme,
    get_system_metrics_scheme,

    # УПРАВЛЕНИЕ СИСТЕМНЫМ ЗВУКОМ
    get_system_volume_scheme,
    set_system_volume_scheme, 
    decrease_volume_scheme,
    increase_volume_scheme,

    # НАВЫКИ, КОТОРЫЕ УПРАВЛЯЮТ МЫШЬЮ И КЛАВИАТУРОЙ
    get_windows_layout_scheme, 
    move_mouse_scheme, 
    current_mouse_coordinates_scheme, 
    click_mouse_scheme, 
    scroll_mouse_scheme, 
    drag_mouse_scheme,
    press_hotkey_scheme, 
    copy_to_clipboard_scheme, 
    write_text_scheme, 
    system_command_scheme, 

    # НАВЫКИ, СВЯЗАННЫЕ С ВЗАИМОДЕЙСТВИЕМ С ПРИЛОЖЕНИЯМИ И ОКНАМИ
    get_processes_scheme, 
    currently_open_windows_scheme,

    # НАВЫКИ ДЛЯ СОЦСЕТЕЙ
    get_telegram_channel_info_scheme,

    # НАВЫКИ, СВЯЗАННЫЕ С МУЗЫКОЙ ИЗ FOOBAR2000
    music_play_random_scheme, 
    music_pause_playback_scheme, 
    music_resume_playback_scheme, 
    music_play_next_track_scheme,
    music_play_previous_track_scheme, 
    music_clear_playlist_scheme, 
    music_play_playlist_scheme, 
    music_play_track_scheme,
    music_play_random_album_scheme,
    all_names_playlists_scheme,
    all_tracks_in_playlist_scheme
    
]

# 3. УКАЗАНИЕ, КАКОЙ НАВЫК ИСПОЛЬЗОВАТЬ (НЕЙРОСЕТЬ БУДЕТ ВЫЗЫВАТЬ КЛЮЧИ (возможно также будет передавать что-либо), И В ДАННОМ СЛУЧАЕ ЗНАЧЕНИЕ КЛЮЧА АКТИВИРУЕТ СООВЕТСТВУЮЩИЙ НАВЫК ДЛЯ ЭТОГО КЛЮЧА)
skills_registry = {
    # БАЗОВЫЕ НАВЫКИ
    "get_weather": assistant_tools.skills.get_weather, # Правильные ключи брать из файла skills_diagrams.py по ключу "name"
    "search_in_google": assistant_tools.skills.search_in_google,
    "get_date": assistant_tools.skills.get_date,
    "get_time": assistant_tools.skills.get_time,
    "make_screenshot": assistant_tools.skills.make_screenshot,
    "save_to_memory": assistant_tools.skills.save_to_memory,
    "lock_pc": assistant_tools.skills.lock_pc,
    "get_habr_news": assistant_tools.skills.get_habr_news,
    "get_system_metrics": assistant_tools.skills.get_system_metrics,

    # УПРАВЛЕНИЕ СИСТЕМНЫМ ЗВУКОМ
    "get_system_volume": assistant_tools.skills.get_system_volume,
    "set_system_volume": assistant_tools.skills.set_system_volume,
    "decrease_volume": assistant_tools.skills.decrease_volume,
    "increase_volume": assistant_tools.skills.increase_volume,

    # НАВЫКИ, КОТОРЫЕ УПРАВЛЯЮТ МЫШЬЮ И КЛАВИАТУРОЙ
    "get_windows_layout": assistant_tools.skills.get_windows_layout, 
    "move_mouse": assistant_tools.skills.move_mouse, 
    "current_mouse_coordinates": assistant_tools.skills.current_mouse_coordinates, 
    "click_mouse": assistant_tools.skills.click_mouse,
    "scroll_mouse": assistant_tools.skills.scroll_mouse, 
    "drag_mouse": assistant_tools.skills.drag_mouse, 
    "press_hotkey": assistant_tools.skills.press_hotkey,
    "copy_to_clipboard": assistant_tools.skills.copy_to_clipboard,
    "write_text": assistant_tools.skills.write_text,
    "system_command": assistant_tools.skills.system_command,

    # НАВЫКИ, СВЯЗАННЫЕ С ВЗАИМОДЕЙСТВИЕМ С ПРИЛОЖЕНИЯМИ И ОКНАМИ
    "get_processes": assistant_tools.skills.get_processes,
    "currently_open_windows": assistant_tools.skills.currently_open_windows,

    # НАВЫКИ ДЛЯ СОЦСЕТЕЙ
    "get_telegram_channel_info": assistant_tools.socialmedia_skills.get_telegram_channel_info,

    # НАВЫКИ, СВЯЗАННЫЕ С МУЗЫКОЙ ИЗ FOOBAR2000
    "music_play_random": assistant_tools.music_skills.music_play_random,
    "music_pause_playback": assistant_tools.music_skills.music_pause_playback,
    "music_resume_playback": assistant_tools.music_skills.music_resume_playback,
    "music_play_next_track": assistant_tools.music_skills.music_play_next_track,
    "music_play_previous_track": assistant_tools.music_skills.music_play_previous_track,
    "music_clear_playlist": assistant_tools.music_skills.music_clear_playlist,
    "music_play_playlist": assistant_tools.music_skills.music_play_playlist,
    "music_play_track": assistant_tools.music_skills.music_play_track,
    "music_play_random_album": assistant_tools.music_skills.music_play_random_album,
    "all_names_playlists": assistant_tools.music_skills.all_names_playlists,
    "all_tracks_in_playlist": assistant_tools.music_skills.all_tracks_in_playlist,
}
