# hotkeys_manager.py
from assistant_brain.brain import litany_of_analysis_screen 
import keyboard
import threading

hotkey_activate_litany_of_analysis_screen = "ctrl+alt+shift+f1"
deactivate_hotkey_manager = "ctrl+shift+alt+f2"

def _setup_hotkeys():
    """Настраивает все глобальные горячие клавиши."""
    keyboard.add_hotkey(hotkey_activate_litany_of_analysis_screen, litany_of_analysis_screen) # Горячая клавиша для "Литании Анализа", просмотра и анализа экрана
    print(f"Hotkey {hotkey_activate_litany_of_analysis_screen} added for function 'litany_of_analysis_screen'.")
    # В будущем можно добавить остальные

def _hotkeys_manager():
    """Главная функция этого модуля - настраиваеть хоткеи и ждать их возможного вызова."""
    print(f"Hotkeys manager is running. Press {deactivate_hotkey_manager} to deactivate hotkeys.")
    _setup_hotkeys()
    
    keyboard.wait(deactivate_hotkey_manager) # Эта функция будет блокировать поток, в котором она запущена, пока не будет нажана горячая клавиша для отмены
    print("Exit hotkey detected. Shutting down...")

def initialize_hotkeys_manager():
    hotkeys_thread = threading.Thread(target=_hotkeys_manager)
    hotkeys_thread.daemon = True # Чтобы он завершился вместе с основной программой
    hotkeys_thread.start()

