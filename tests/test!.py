import pyautogui
import os
import google.generativeai as genai
from PIL import Image 
from dotenv import load_dotenv

def make_screenshot():
    filename = "screenshot.png"
    try:
        screenshot = pyautogui.screenshot(filename)  
        screenshot.save(filename)  
        print({"status": "success", "file_path": os.path.abspath(filename)})
        return {"status": "success", "file_path": os.path.abspath(filename)}
    
    except Exception as e:
        print({"status": "error", "message": str(e)})
        return {"status": "error", "message": str(e)}
    

make_screenshot()

load_dotenv() # для загрузки API ключей из .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# 1. Указываем путь к скриншоту
screenshot_path = "screenshot.png" # Предполагаем, что скриншот уже сделан и сохранен

try:
    # 2. Открываем изображение
    img = Image.open(screenshot_path)

    # 3. Выбираем мультимодальную модель
    model = genai.GenerativeModel('gemini-2.0-flash')

    # 4. Создаем промпт, который включает и текст, и изображение
    prompt_text = """
    Проанализируй этот скриншот. 
    Опиши, что происходит на экране? 
    Если есть какой-то код или текст ошибки, извлеки его дословно.
    """
    
    # 5. Отправляем запрос
    response = model.generate_content([prompt_text, img]) # <-- САМОЕ ВАЖНОЕ: передаем список [текст, картинка]

    print("--- Ответ от Gemini Vision ---")
    print(response.text)
    print("----------------------------")

except FileNotFoundError:
    print(f"Ошибка: файл '{screenshot_path}' не найден.")
except Exception as e:
    print(f"Произошла ошибка: {e}")
