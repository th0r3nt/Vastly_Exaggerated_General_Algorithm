# utils.py
import random
import pygame
import time
import os

# --- КОНФИГУРАЦИЯ ЗВУКОВ ---
SFX_DIR = 'assistant_sounds'  # Папка со звуковыми файлами
SFX_CONFIG = { # Ключ: название звуков (смотреть в папке assistant_sounds) без .mp3, значение: количество звуков в этой категории (смотреть на название звука, последний символ - номер звука)
    'general_system_startup': 1, # Для запуска всей системы
    'select': 3,
    'hard_processing': 1,
    'start_additional_system': 4, # Для запуска отдельных элементов
    'processing': 2,
    'search': 2,
    'error': 7,
    'silent_execution': 6,
    'access_error': 2,
    'access_critical_error': 1,
    'execution': 2,
    'notification': 2,
    'silent_error': 1,
    'warning': 2,
    'unknown_command': 1,
}


SOUNDS = {} # Словарь, автоматически создаваемый функцией _init_sounds, выглядит как {'system_startup': (assistant_sounds/system_startup1.mp3, assistant_sounds/system_startup2.mp3, ...), ...}
SOUND_CACHE = {} # Кэш, чтобы не грузить файлы с диска каждый раз

def _init_sounds():
    """Автоматически генерирует словарь SOUNDS на основе конфига."""
    global SOUNDS
    for category, value in SFX_CONFIG.items():
        if isinstance(value, int):
             SOUNDS[category] = tuple(os.path.join(SFX_DIR, f"{category}{i}.mp3") for i in range(1, value + 1)) # range(1, value + 1)) означает: от звука номер 1 и до value (самого последнего) включительно создавать 1 путь, который ведет к звуку
        elif isinstance(value, (list, tuple)):
             SOUNDS[category] = tuple(value)

try:
    # Pre-init может помочь убрать задержку перед первым звуком
    pygame.mixer.pre_init(44100, -16, 2, 1024)
    pygame.mixer.init()
    pygame.mixer.set_num_channels(32) # Разрешаем много одновременных звуков
    _init_sounds()
    print(f"Audio system initialized. Loaded {len(SOUNDS)} sound categories.")
except pygame.error as e:
    print(f"Fatal error: Could not initialize pygame mixer. Error: {e}")
    pygame = None

def play_sfx(sound_name: str, volume: float = 1.0):
    """Проигрывает случайный звук из указанной категории. Не блокирует основной поток."""
    if not pygame or not sound_name:
        return

    if sound_name not in SOUNDS:
        print(f"Warning: Sound category '{sound_name}' not found.")
        return

    try:
        file_path = random.choice(SOUNDS[sound_name])
    
        if file_path not in SOUND_CACHE:
            SOUND_CACHE[file_path] = pygame.mixer.Sound(file_path)
        
        sound = SOUND_CACHE[file_path]
        sound.set_volume(volume)
        time.sleep(0.2)
        sound.play()
        
    except Exception as e:
        # Отлавливаем ошибки (например, файла физически нет на диске)
        print(f"Error playing sfx '{sound_name}' (path: {file_path}): {e}")

if __name__ == "__main__":
    print("Sound Utils Test Mode. Type category name to play.")
    while True:
        cmd = input(">> ").strip()
        if cmd.lower() in ['exit', 'quit']: 
            break
        play_sfx(cmd)
        time.sleep(0.05) # Небольшая пауза для UI