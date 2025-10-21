# skills.py
import threading
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
import keyboard
import logging
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import pythoncom
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from assistant_general.logger_config import setup_logger
from assistant_tools.utils import play_sfx
from assistant_vector_database.database import add_new_memory
from bs4 import BeautifulSoup
import wmi
from PIL import Image 
from pyrogram import Client

setup_logger()
logger = logging.getLogger(__name__)

load_dotenv() # для загрузки API ключей из .env
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHER_CITY_LAT = os.getenv("WEATHER_CITY_LAT")
WEATHER_CITY_LON = os.getenv("WEATHER_CITY_LON")
OPENHARDWAREMONITOR_PATH = os.getenv("OPENHARDWAREMONITOR_PATH")

MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")

# ДЛЯ РЕГИСТРАЦИИ НОВЫХ НАВЫКОВ В ВЕГУ НУЖНО:
# Написать json схему в skills_diagrams.py
# Перейти в assistant_brain.added_skills.py и следовать инструкциям, которые описаны в файле файла

def get_weather(city_name: str = None):
    """Получает текущую погоду"""
    play_sfx('silent_execution')
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

    final_answer = f"City: {sity_name}; Weather description: {weather_description}; Feels like: {description_of_feeling_temp}°; Actual temperature: {description_of_temp}°; Air humidity: {humidity}; Wind: {wind} m/s."
    logger.debug(final_answer)
    return final_answer

def search_in_google(search_query: str) -> str:
    """Ищет переданный запрос в поисковике и открывает вкладку браузера."""
    play_sfx('silent_execution')
    if not search_query:
        logger.error("Error: A search query is required to search.")
        play_sfx('silent_error')
        return "Error: A search query is required to search."
    webbrowser.open(f"https://yandex.ru/search/?text={search_query}") #Альтернативно https://www.google.com/search?q=
    logger.debug(f"The search page for the query is open: '{search_query}'.")
    return f"The search page for the query is open: '{search_query}'."

def get_time(**kwargs) -> str:
    """Возвращает текущее время в формате ЧЧ:ММ."""
    play_sfx('silent_execution')
    now = datetime.datetime.now()
    return f"Current time: {now.strftime('%H:%M')}."

def get_date() -> str:
    """Возвращает сегодняшнюю дату."""
    play_sfx('silent_execution')
    now = datetime.datetime.now()
    return f"Today {now.day} {MONTHS[now.month - 1]}."

def make_screenshot():
    """Делает скриншот и сохраняет его в папку 'assistant_temporary_files'. Папка создается автоматически, если ее нет."""
    # Определяем имя папки и имя файла
    play_sfx('silent_execution')
    temp_folder = "assistant_temporary_files"
    filename = "screenshot.png"
    
    full_path = os.path.join(temp_folder, filename) # os.path.join() - правильный способ соединять пути
    try:
        # Проверяем, существует ли папка, и создаем ее, если нет
        os.makedirs(temp_folder, exist_ok=True) # exist_ok=True означает, что ошибки не будет, если папка уже существует
        
        # 4. Делаем скриншот и сохраняем его сразу по полному пути
        screenshot = pyautogui.screenshot(full_path)
        screenshot.save(full_path)

        logger.info(f"Screenshot saved at: {os.path.abspath(full_path)}")
        return {"status": "success", "file_path": os.path.abspath(full_path)} # Возвращаем абсолютный путь
    
    except Exception as e:
        logger.error(f"Failed to create screenshot: {e}") 
        play_sfx('silent_error')
        return {"status": "error", "message": str(e)}
    
def get_screenshot_context():
    """Делает скриншот и возвращает объект Image, либо None в случае ошибки."""
    play_sfx('silent_execution')
    try:
        screenshot_info = make_screenshot()
        if screenshot_info['status'] == 'success':
            screenshot_path = screenshot_info['file_path']
            img = Image.open(screenshot_path)
            logger.info(f"Screenshot taken: {screenshot_path}")
            play_sfx('silent_execution')
            return img # Возвращаем само изображение
        else:
            logger.error(f"Failed to take screenshot: {screenshot_info['message']}")
            play_sfx('silent_error')
            return None 
    except Exception as e:
        logger.error(f"Error creating or opening screenshot: {e}")
        play_sfx('silent_error')
        return None 
    
def save_to_memory(text):
    """Сохраняет в память любой факт о пользователе."""
    play_sfx('silent_execution')
    add_new_memory(text)
    logger.debug(f"Record '{text}'save to memory.")
    return "Record save to memory."

def lock_pc():
    """Блокирует рабочую станцию Windows."""
    play_sfx('silent_execution')
    if platform.system() == "Windows":
        try:
            ctypes.windll.user32.LockWorkStation()
            logger.debug("The workstation is locked.")
            play_sfx('silent_execution')
            return "The workstation is locked"
        except Exception as e:
            logger.error(f"Unable to lock workstation. Error: {e}")
            play_sfx('silent_error')
            return f"Unable to lock workstation. Error: {e}"
    else:
        # Если Вега запустится на Linux или macOS в будущем
        logger.debug("The command only works on the Windows operating system.")
        play_sfx('silent_error')
        return "The command only works on the Windows operating system."
    
def get_system_volume() -> str: # Возвращаемый тип изменен на str, как у вас в коде
    """Возвращает текущую системную громкость в процентах (от 0 до 100)."""
    play_sfx('silent_execution')
    # Инициализируем COM для текущего потока
    pythoncom.CoInitialize()
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_control = cast(interface, POINTER(IAudioEndpointVolume))
        
        current_volume_scalar = volume_control.GetMasterVolumeLevelScalar()
        current_volume_percent = int(current_volume_scalar * 100)

        logger.debug(f"Current system volume: {current_volume_percent}%")
        return f"Current volume: {current_volume_percent}%" # Лучше возвращать с % для ясности
    except Exception as e:
        logger.error(f"Ошибка при получении информации о текущей громкости: {e}")
        play_sfx('silent_error')
        return f"Ошибка при получении информации о текущей громкости: {e}"
    finally:
        # Обязательно деинициализируем COM перед выходом из потока/функции
        pythoncom.CoUninitialize()

def set_system_volume(level_volume: int) -> str: # Возвращаемый тип изменен на str
    """Принимает число от 0 до 100 и выставляет такую системную громкость."""
    play_sfx("silent_execution")
    if not 0 <= level_volume <= 100:
        play_sfx("silent_error")
        return f"Громкость должна быть между 0 и 100, а не {level_volume}"

    # Инициализируем COM для текущего потока
    pythoncom.CoInitialize()
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_control = cast(interface, POINTER(IAudioEndpointVolume))
        
        target_volume_scalar = level_volume / 100.0
        volume_control.SetMasterVolumeLevelScalar(target_volume_scalar, None)
        
        print(f"Volume changed to {level_volume}%.")
        return f"Громкость изменена на {level_volume}%."
    except Exception as e:
        print(f"Error when changing volume: {e}")
        play_sfx("silent_error")
        return f"Ошибка при изменении громкости: {e}"
    finally:
        # Обязательно деинициализируем COM
        pythoncom.CoUninitialize()

def decrease_volume(amount: int = 10):
    """Уменьшает системную громкость на указанное значение в процентах. Возвращает новую громкость в процентах."""
    pythoncom.CoInitialize()
    play_sfx("silent_execution")
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_control = cast(interface, POINTER(IAudioEndpointVolume))
        
        current_volume_scalar = volume_control.GetMasterVolumeLevelScalar() # Получаем текущую громкость
        
        decrease_scalar = amount / 100.0 # Правильно вычисляем целевую громкость, 10 превратится в 0.1
        target_volume_scalar = max(0.0, current_volume_scalar - decrease_scalar) # Текущая - указанная
        
        volume_control.SetMasterVolumeLevelScalar(target_volume_scalar, None) # Устанавливаем новую громкость
        
        new_volume_percent = int(target_volume_scalar * 100)
        return f"Volume successfully decreased to {new_volume_percent}%."

    except Exception as e:
        play_sfx("silent_error")
        return f"Error when changing volume: {e}"   
    finally:
        pythoncom.CoUninitialize()

def increase_volume(amount: int = 10):
    """Увеличивает системную громкость на указанное значение в процентах. Возвращает новую громкость в процентах."""
    play_sfx("silent_execution")
    pythoncom.CoInitialize()
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_control = cast(interface, POINTER(IAudioEndpointVolume))
        
        current_volume_scalar = volume_control.GetMasterVolumeLevelScalar() # Получаем текущую громкость
        increase_scalar = amount / 100.0 # Правильно вычисляем целевую громкость, 10 превратится в 0.1

        target_volume_scalar = min(1.0, current_volume_scalar + increase_scalar) # Текущая + указанная
        
        volume_control.SetMasterVolumeLevelScalar(target_volume_scalar, None) # Устанавливаем новую громкость
        
        new_volume_percent = int(target_volume_scalar * 100)
        return f"Volume successfully increased to {new_volume_percent}%."

    except Exception as e:
        play_sfx("silent_error")
        return f"Error when changing volume: {e}"   
    finally:
        pythoncom.CoUninitialize()

def get_habr_news(limit=10):
    """Получает топ статей с Habr.com."""
    play_sfx("silent_execution")
    url = 'https://habr.com/ru/all/'  # Главная страница с новыми статьями
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }  # Имитация браузера, чтобы избежать блокировок
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверка на HTTP-ошибки
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.find_all('article', class_='tm-articles-list__item')[:limit] # Поиск контейнеров статей (класс 'tm-articles-list__item')
        
        result = []
        for article in articles:
            # Заголовок и ссылка
            title_elem = article.find('a', class_='tm-title__link')
            title = title_elem.text.strip() if title_elem else 'N/A'
            link = 'https://habr.com' + title_elem['href'] if title_elem else 'N/A'
            
            # Краткое описание
            summary_elem = article.find('div', class_='article-formatted-body')
            summary = summary_elem.text.strip()[:200] + ' (text truncated for brevity)...' if summary_elem else 'N/A'
            
            result.append({
                'title': title,
                'link': link,
                'summary': summary
            })

        # for i, art in enumerate(result, 1):
        #     print(f"{i}. {art['title']}\n   Ссылка: {art['link']}\n   Кратко: {art['summary']}\n") # ДЛЯ ОТЛАДКИ

        play_sfx("silent_execution")
        return result
    
    except requests.RequestException as e:
        logger.error(f"Error requesting page: {e}")
        play_sfx("silent_error")
        return []
    except Exception as e:
        logger.error(f"Parsing error: {e}")
        play_sfx("silent_error")
        return []

def get_system_metrics():
    """Возвращает текущую нагрузку процессора, видеокарты и оперативной памяти один раз. 
    Требует открытого OpenHardwareMonitor."""
    play_sfx("silent_execution")
    try:
        w = wmi.WMI(namespace="root\OpenHardwareMonitor")
        sensors = w.Sensor()
        if not sensors:
            logger.info("No sensors are available. OpenHardwareMonitor may not be running.")
            return "No sensors are available. OpenHardwareMonitor may not be running. Needs to be launched."

        cpu_temp = None
        cpu_load = None
        gpu_temp = None
        gpu_load = None
        ram_load = None

        # Ищем нужные сенсоры
        for sensor in sensors:
            if sensor.SensorType == "Temperature" and sensor.Name == "Temperature":
                cpu_temp = sensor.Value
            elif sensor.SensorType == "Load" and sensor.Name == "CPU Total":
                cpu_load = sensor.Value
            elif sensor.SensorType == "Temperature" and sensor.Name == "GPU Core":
                gpu_temp = sensor.Value
            elif sensor.SensorType == "Load" and sensor.Name == "GPU Core":
                gpu_load = sensor.Value
            elif sensor.SensorType == "Load" and sensor.Name == "Memory":
                ram_load = sensor.Value

        # Форматируем значения
        cpu_temp = f"{cpu_temp:.1f}°C" if cpu_temp is not None else "Недоступно"
        cpu_load = f"{cpu_load:.1f}%" if cpu_load is not None else "Недоступно"
        gpu_temp = f"{gpu_temp:.1f}°C" if gpu_temp is not None else "Недоступно"
        gpu_load = f"{gpu_load:.1f}%" if gpu_load is not None else "Недоступно"
        ram_load = f"{ram_load:.1f}%" if ram_load is not None else "Недоступно"
        now = datetime.now()

        # Вывод в одну строку
        output = (f"Readings from the main PC sensors ({now.strftime('%H:%M:%S')}): \nCPU: {cpu_temp}, {cpu_load}; \nGPU: {gpu_temp}, {gpu_load}; \nRAM: {ram_load}")
        
        return output
    
    except Exception as e:
        logger.error(f"Error: {str(e)}. Make sure OpenHardwareMonitor is running.")
        play_sfx("silent_error")
        return f"Error: {str(e)}. Make sure OpenHardwareMonitor is running."
    
# УПРАВЛЕНИЕ ПК, МЫШЬ, КЛАВИАТУРА 

def get_windows_layout():
    """Возвращает текущую раскладку клавиатуры в Windows. Возвращает строку вроде "ENG","RUS" и прочее."""
    play_sfx("silent_execution")
    if platform.system() != "Windows":
        play_sfx("silent_error")
        return "Not a Windows system"

    # Словарь популярных раскладок. Полный список можно найти по запросу "Windows Language Code Identifier"
    layouts = {
        0x409: "ENG", 0x419: "RUS", 0x407: "GER",
        0x40C: "FRA", 0x410: "ITA", 0x411: "JPN", 
        0x412: "KOR", 0x804: "CHN" 
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
    play_sfx("silent_execution")
    pyautogui.moveTo(x, y, duration=0.05)
    logger.debug(f"The mouse is moved to coordinates: {x}, {y}")
    return f"The mouse is moved to coordinates: {x}, {y}"

def current_mouse_coordinates():
    "Определяет текущие координаты мыши."
    play_sfx("silent_execution")
    current_position = pyautogui.position()
    logger.debug(f"The mouse is currently at X={current_position.x}, Y={current_position.y}")
    return f"The mouse is currently at X={current_position.x}, Y={current_position.y}"

def click_mouse(button='left', clicks=1, interval=0.1):
    """Кликнуть мышью. Левой, правой, одинарный, двойной - на выбор."""
    play_sfx("silent_execution")
    pyautogui.click(button=button, clicks=clicks, interval=interval)
    logger.debug(f"Performed {clicks} click(s) with the {button} mouse button.")
    return f"Performed {clicks} click(s) with the {button} mouse button."

def scroll_mouse(amount):
    """Скроллит вверх (положительное число) или вниз (отрицательное)."""
    play_sfx("silent_execution")
    pyautogui.scroll(amount)
    direction = "up" if amount > 0 else "down"
    logger.debug(f"Scrolled {abs(amount)} units {direction}.")
    return f"Scrolled {abs(amount)} units {direction}."

def drag_mouse(x_to, y_to, duration=0.5):
    """Тащит мышь из текущей позиции в точку (x, y), как будто что-то выделяет."""
    pyautogui.dragTo(x_to, y_to, duration=duration)
    logger.debug(f"Dragged mouse to {x_to}, {y_to}.")
    play_sfx("silent_execution")
    return f"Dragged mouse to {x_to}, {y_to}."
    
def press_hotkey(keys):
    """Нажимает любое количество горячих клавиш. Например: ('ctrl', 'shift', 'esc')"""
    play_sfx("silent_execution")
    pyautogui.hotkey(*keys)
    logger.debug(f"Hotkey pressed: {' + '.join(keys)}")
    return f"Hotkey pressed: {' + '.join(keys)}"

def copy_to_clipboard(text):
    """Копирует любой текст в буфен обмена."""
    play_sfx("silent_execution")
    pyperclip.copy(text)
    logger.debug(f"Text '{text}' copied to clipboard.")
    return f"Text '{text}' copied to clipboard."

def write_text(text, attempts=0):
    """Печатает любой текст, даже на эльфийском."""
    play_sfx("silent_execution")
    keyboard.write(text)
    

def system_command(command):
    """Выполняет системные команды. Выключение, перезагрузка. ОПАСНО."""
    play_sfx("silent_execution")
    # Примеры команд для Windows:
    # 'shutdown /s /t 1' - выключить пк через 1 секунду, 'shutdown /r /t 1' - перезагрузить пк через 1 секунду, 'rundll32.exe powrprof.dll,SetSuspendState 0,1,0' - отправить в спящий режим
    os.system(command)
    logger.info(f"Executing system command: {command}.")
    return f"Executing system command: {command}."

# ОКНА, ПРОГРАММЫ, ПРИЛОЖЕНИЯ 

def get_processes():
    """Сканирует систему и возвращает только полезный список процессов, отфильтровав все ненужные/системные."""
    play_sfx("silent_execution")
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
    play_sfx("silent_execution")
    titles = []
    all_titles = gw.getAllTitles()
    for title in all_titles:
        if title: # Игнорируем пустые заголовки
            titles.append(title)
    return titles
    



