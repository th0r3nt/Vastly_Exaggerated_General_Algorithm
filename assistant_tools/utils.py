# utils.py
import random 
import threading
import pygame
import time

SOUNDS = {
    'system_startup': ('sounds/system_startup1.mp3',),
    'select': ('sounds/select1.mp3',),
    'confirmation': ('sounds/confirmation1.mp3',),
    'processing': ('sounds/processing1.mp3',),
    'hard_processing': ('sounds/hard_processing1.mp3',),
    'search': ('sounds/search1.mp3',),
    'mechanical_movement': ('mechanical_movement1.mp3',),
    'lauch_vector_database': ('sounds/lauch_vector_database1.mp3',), 
    'start_embedding_model': ('sounds/start_embedding_model1.mp3',), 

    'error': ('sounds/error1.mp3', 'sounds/error2.mp3', 'sounds/error3.mp3', 'sounds/error4.mp3', 'sounds/error5.mp3', 'sounds/error6.mp3',), # ПОНАСТАВЛЯТЬ ЗВУКИ
}

try:
    pygame.mixer.init()
    print("Pygame mixer initialized successfully.")
except pygame.error as e:
    print(f"Fatal error: Could not initialize pygame mixer. Sound will be disabled. Error: {e}")
    pygame = None # Отключаем pygame, если он не смог запуститься

def _play_sound_worker(sound_name: str):
    if sound_name in SOUNDS:
        sounds = SOUNDS[sound_name] 
        pygame.mixer.music.load(random.choice(sounds))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy(): # Ждать окончания
            time.sleep(1)
    else:
        print("Error: Non-existent sound selected for function 'play_sfx()'.")

def play_sfx(sound_name: str):
    if not sound_name:
        return

    sound_worker_thread = threading.Thread(target=_play_sound_worker, kwargs={"sound_name": sound_name,}) # Создаем, собственно, отдельный поток
    sound_worker_thread.start()
