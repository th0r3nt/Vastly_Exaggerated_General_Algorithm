# skills.py
import webbrowser
import requests
import datetime
import pyautogui  
import os
from dotenv import load_dotenv
import ctypes
import platform
import pyperclip
import pygetwindow as gw
import psutil
import os
import keyboard
import logging
from assistant_general.logger_config import setup_logger
from assistant_vector_database.database import add_new_memory

setup_logger()
logger = logging.getLogger(__name__)

load_dotenv() # для загрузки API ключей из .env
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHER_CITY_LAT = os.getenv("WEATHER_CITY_LAT")
WEATHER_CITY_LON = os.getenv("WEATHER_CITY_LON")

MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")

# ДЛЯ РЕГИСТРАЦИИ НОВЫХ НАВЫКОВ В ВЕГУ НУЖНО:
# Написать json схему в skills_diagrams.py
# Перейти в assistant_brain.added_skills.py и следовать инструкциям, которые описаны в файле файла

def get_weather(city_name: str = None):
    """Получает текущую погоду"""
    if city_name:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
    else: # Если город не передан, узнаем по умолчанию в Липецке
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={WEATHER_CITY_LAT}&lon={WEATHER_CITY_LON}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"

    response = requests.get(url)
    weather_data = response.json()
    weather_description = weather_data["weather"][0]["description"] # Например, "пасмурно"
    description_of_feeling_temp = int(weather_data["main"]["feels_like"])
    description_of_temp = int(weather_data["main"]["temp"])
    humidity = int(weather_data["main"]["humidity"]) # Влажность, например, 36

    wind = weather_data["wind"]["speed"] # Скорость ветра, например, 4.64
    sity_name = weather_data["name"]

    final_answer = f"City: {sity_name}; \nWeather description: {weather_description}; \nFeels like: {description_of_feeling_temp}°; \n Actual temperature: {description_of_temp}°; \n Air humidity: {humidity}; \n Wind: {wind} m/s."
    print(final_answer)
    return final_answer

def search_in_google(search_query: str) -> str:
    """Ищет переданный запрос в поисковике и открывает вкладку браузера."""
    if not search_query:
        logger.error("Error: A search query is required to search.")
        return "Error: A search query is required to search."
    webbrowser.open(f"https://yandex.ru/search/?text={search_query}") #Альтернативно https://www.google.com/search?q=
    logger.debug(f"The search page for the query is open: '{search_query}'.")
    return f"The search page for the query is open: '{search_query}'."

def get_time(**kwargs) -> str:
    """Возвращает текущее время в формате ЧЧ:ММ."""
    now = datetime.datetime.now()
    return f"Current time: {now.strftime('%H:%M')}."

def get_date() -> str:
    """Возвращает сегодняшнюю дату."""
    now = datetime.datetime.now()
    return f"Today {now.day} {MONTHS[now.month - 1]}."

def make_screenshot():
    filename = "screenshot.png"
    try:
        screenshot = pyautogui.screenshot(filename)  
        screenshot.save(filename)  
        return {"status": "success", "file_path": os.path.abspath(filename)}
    
    except Exception as e:
        logger.error({"status": "error", "message": str(e)})
        return {"status": "error", "message": str(e)}
    
def save_to_memory(text):
    """Сохраняет в память любой факт о пользователе."""
    add_new_memory(text)
    logger.debug(f"Record '{text}'save to memory.")
    return "Record save to memory."

def lock_pc():
    """Блокирует рабочую станцию Windows."""
    if platform.system() == "Windows":
        try:
            ctypes.windll.user32.LockWorkStation()
            return "The workstation is locked"
        except Exception as e:
            logger.error(f"Unable to lock workstation. Error: {e}")
            return f"Unable to lock workstation. Error: {e}"
    else:
        # Если Вега запустится на Linux или macOS в будущем
        logger.debug("The command only works on the Windows operating system.")
        return "The command only works on the Windows operating system."
    
# УПРАВЛЕНИЕ ПК, МЫШЬ, КЛАВИАТУРА

def get_windows_layout():
    """
    Возвращает текущую раскладку клавиатуры в Windows.
    Возвращает строку вроде "ENG","RUS" и прочее.
    """
    if platform.system() != "Windows":
        return "Not a Windows system"

    # Словарь популярных раскладок. Полный список можно найти по запросу "Windows Language Code Identifier"
    layouts = {
        0x409: "ENG",
        0x419: "RUS",
        0x407: "GER",
        0x40C: "FRA",
        0x410: "ITA",
        0x411: "JPN", 
        0x412: "KOR", 
        0x804: "CHN" 
    }

    # Загружаем библиотеку user32.dll
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    hwnd = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(hwnd, None)
    layout_id = user32.GetKeyboardLayout(thread_id)
    language_id = layout_id & 0xFFFF

    logger.debug(layouts.get(language_id, f"Unknown layout (ID: {hex(language_id)})"))
    return layouts.get(language_id, f"Unknown layout (ID: {hex(language_id)})")

def move_mouse(x, y):
    "Двигает мышь в указанном направлении."
    pyautogui.moveTo(x, y, duration=0.05)
    logger.debug(f"The mouse is moved to coordinates: {x}, {y}")
    return f"The mouse is moved to coordinates: {x}, {y}"

def current_mouse_coordinates():
    "Определяет текущие координаты мыши."
    current_position = pyautogui.position()
    logger.debug(f"The mouse is currently at X={current_position.x}, Y={current_position.y}")
    return f"The mouse is currently at X={current_position.x}, Y={current_position.y}"

def click_mouse(button='left', clicks=1, interval=0.1):
    """Кликнуть мышью. Левой, правой, одинарный, двойной - на выбор."""
    pyautogui.click(button=button, clicks=clicks, interval=interval)
    logger.debug(f"Performed {clicks} click(s) with the {button} mouse button.")
    return f"Performed {clicks} click(s) with the {button} mouse button."

def scroll_mouse(amount):
    """Скроллит вверх (положительное число) или вниз (отрицательное)."""
    pyautogui.scroll(amount)
    direction = "up" if amount > 0 else "down"
    logger.debug(f"Scrolled {abs(amount)} units {direction}.")
    return f"Scrolled {abs(amount)} units {direction}."

def drag_mouse(x_to, y_to, duration=0.5):
    """Тащит мышь из текущей позиции в точку (x, y), как будто что-то выделяет."""
    pyautogui.dragTo(x_to, y_to, duration=duration)
    logger.debug(f"Dragged mouse to {x_to}, {y_to}.")
    return f"Dragged mouse to {x_to}, {y_to}."
    
def press_hotkey(*keys):
    """Нажимает любое количество горячих клавиш. Например: ('ctrl', 'shift', 'esc')"""
    pyautogui.hotkey(*keys)
    logger.debug(f"Hotkey pressed: {' + '.join(keys)}")
    return f"Hotkey pressed: {' + '.join(keys)}"

def copy_to_clipboard(text):
    """Копирует любой текст в буфен обмена."""
    pyperclip.copy(text)
    logger.debug(f"Text '{text}' copied to clipboard.")
    return f"Text '{text}' copied to clipboard."

def write_text(text, attempts=0):
    """Печатает любой текст, даже на эльфийском."""
    keyboard.write(text)

def system_command(command):
    """Выполняет системные команды. Выключение, перезагрузка. ОПАСНО."""
    # Примеры команд для Windows:
    # 'shutdown /s /t 1' - выключить пк через 1 секунду, 'shutdown /r /t 1' - перезагрузить пк через 1 секунду, 'rundll32.exe powrprof.dll,SetSuspendState 0,1,0' - отправить в спящий ре'Проверка.'жим
    os.system(command)
    logger.info(f"Executing system command: {command}.")
    return f"Executing system command: {command}."

# --- ОКНА, ПРОГРАММЫ, ПРИЛОЖЕНИЯ ----

def get_filtered_processes():
    """Сканирует систему и возвращает только полезный список процессов, отфильтровав все ненужные/системные."""
    # Сюда кладем все системные процессы, которые нам нужны
    system_processes_blacklist = [
        "svchost.exe", "lsass.exe", "csrss.exe", "wininit.exe", "services.exe", "winlogon.exe", "dwm.exe", "spoolsv.exe",
        "explorer.exe", "rundll32.exe", "ctfmon.exe", "fontdrvhost.exe", "conhost.exe", "sihost.exe", "taskhostw.exe", "RuntimeBroker.exe",
        "ApplicationFrameHost.exe", "SearchHost.exe", "ShellExperienceHost.exe", "StartMenuExperienceHost.exe", "SystemSettings.exe", "backgroundTaskHost.exe",
        "unsecapp.exe", "System", "System Idle Process", "SecurityHealthSystray.exe", "nvcontainer.exe", "steamwebhelper.exe", "lghub_agent.exe", 
        "msedgewebview2.exe", "OneDrive.Sync.Service.exe", "CrossDeviceResume.exe", "LockApp.exe", "ShellHost.exe", "UserOOBEBroker.exe",
        "WebViewHost.exe", "WidgetService.exe", "Widgets.exe", "XboxPcApp.exe", "XboxPcAppFT.exe", "XboxPcTray.exe", "lghub_system_tray.exe",
        "ruff.exe", "winws.exe"
    ]
    filtered_list = []

    # Получаем имя текущего пользователя, чтобы отсеять процессы других юзеров
    current_user = os.getlogin()

    for process in psutil.process_iter(['pid', 'name', 'username']):
        try:
            proc_info = process.info
            proc_name = proc_info['name']
            proc_user = proc_info['username']

            if not proc_user: # Отсеиваем процессы, у которых нет имени пользователя (обычно это системные)
                continue
            if current_user not in proc_user and 'SYSTEM' not in proc_user: # Оставляем только процессы текущего пользователя
                continue
            if proc_name.lower() in [p.lower() for p in system_processes_blacklist]: # Отсеиваем всё из нашего чёрного списка (без учёта регистра)
                continue

            # Если процесс прошёл все круги ада, добавляем его в список
            filtered_list.append(proc_name)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Возвращаем уникальный список, чтобы не было дубликатов
    # (например, 10 процессов chrome.exe превратятся в один)
    logger.debug(f"Current processes in system: {sorted(list(set(filtered_list)))}")
    return f"Current processes in system: {sorted(list(set(filtered_list)))}"

def currently_open_windows():
    """Возвращает текущие окна, которые открыты."""
    titles = []
    all_titles = gw.getAllTitles()
    for title in all_titles:
        if title: # Игнорируем пустые заголовки
            titles.append(title)
    return titles
    
def manage_window(title, action='activate'):
    """Находит окно по заголовку и дает возможность провести разные команды: activate, minimize, maximize, close."""
    try:
        # Ищем окно, заголовок которого СОДЕРЖИТ указанный текст
        windows = gw.getWindowsWithTitle(title)
        if windows:
            win = windows[0]
            if action == 'activate':
                win.activate()
            elif action == 'minimize':
                win.minimize()
            elif action == 'maximize':
                win.maximize()
            elif action == 'close':
                win.close()
            logger.debug(f"Window '{title}' action '{action}' executed.")
            return f"Window '{title}' action '{action}' executed."
        else:
            logger.info(f"Window with title '{title}' not found.")
            return f"Window with title '{title}' not found."
    except IndexError:
        logger.error(f"ERROR: No window with title '{title}' found.")
        return f"ERROR: No window with title '{title}' found."
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}"
    
# --- УПРАВЛЕНИЯ ПРОГРАММАМИ И ПРИЛОЖЕНИЯМИ ---

def open_program(path_to_exe):
    """Открывает программу или файл по указанному пути."""
    try:
        os.startfile(path_to_exe)
        return f"Starting the program at {path_to_exe}."
    except Exception as e:
        return f"Failed to start the program: {str(e)}"
    
def kill_process_by_name(process_name):
    """Находит и безжалостно убивает процесс по его имени."""
    # /f - force, /im - image name
    os.system(f"taskkill /f /im {process_name}") 
    logger.info(f"Sent a kill command to {process_name}.")
    return f"Sent a kill command to {process_name}."


# os.listdir(path) — посмотреть, что лежит в папке.
# os.mkdir(path) — создать папку.
# os.remove(path) — удалить файл.
# shutil.move(src, dst) — переместить/переименовать.

# import shutil

# def list_directory_contents(path="."):
#     """Возвращает список файлов и папок в указанной директории."""
#     return str(os.listdir(path))

# def create_directory(path):
#     """Создаёт новую папку."""
#     os.makedirs(path, exist_ok=True) # exist_ok=True - чтобы не было ошибки, если папка уже есть
#     return f"Directory {path} created."

# def delete_path(path):
#     """Удаляет файл или папку со всем её содержимым. ПИЗДЕЦ КАК ОПАСНО."""
#     if os.path.isfile(path):
#         os.remove(path)
#     elif os.path.isdir(path):
#         shutil.rmtree(path)
#     return f"Path {path} has been deleted."

# if __name__ == "__main__":
#     import time  # noqa: F401
#     print("ТЕСТЫ ВЗАИМОДЕЙСТВИЯ С МЫШКОЙ, КОПИРОВАНИЕМ И КЛАВИАТУРОЙ")
#     manage_window("Steam", "activate")
#     currently_open_windows()



# #3: "ШЁПОТ, СУКА!" (Volume Control)
# Твоя Вега может включить тебе Foobar2000, но она, блядь, не может СДЕЛАТЬ ПОГРОМЧЕ! Или, что важнее, ЗАМЬЮТИТЬ, НАХУЙ, ВСЁ, когда тебе звонит мама!
# РЕШЕНИЕ: Библиотека pycaw (pip install pycaw). Она сложная, как ебаный адронный коллайдер, но даёт полный, сука, контроль над звуком!
# code
# Python
# # ЭТО СЛОЖНЫЙ, БЛЯДЬ, ПРИМЕР!
# from ctypes import cast, POINTER
# from comtypes import CLSCTX_ALL
# from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# def set_system_volume(level):
#     """Устанавливает системную громкость от 0.0 до 1.0."""
#     devices = AudioUtilities.GetSpeakers()
#     interface = devices.Activate(
#         IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
#     volume = cast(interface, POINTER(IAudioEndpointVolume))
#     volume.SetMasterVolumeLevelScalar(level, None)
#     return f"System volume set to {level * 100}%."

# def mute_system(mute_status):
#     """Мьютит (True) или размьючивает (False) систему."""
#     # ... (код похожий, ищи в доках pycaw) ...