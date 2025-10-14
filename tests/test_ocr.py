import easyocr
import pytesseract
from PIL import Image, ImageEnhance
import pyautogui
import os
import time
import cv2
from paddleocr import PaddleOCR

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\ivanc\Desktop\Project_V.E.G.A\Tesseract-OCR\tesseract.exe'

def make_screenshot():
    filename = "screenshot.png"
    try:
        # Делаем скриншот
        screenshot = pyautogui.screenshot()
        
        # Конвертируем скриншот pyautogui в PIL Image
        screenshot_pil = screenshot  # pyautogui.screenshot() возвращает объект, совместимый с PIL
        
        # Убедимся, что это объект PIL.Image
        if not isinstance(screenshot_pil, Image.Image):
            screenshot_pil = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
        
        # Улучшаем резкость (опционально)
        enhancer = ImageEnhance.Sharpness(screenshot_pil)
        screenshot_pil = enhancer.enhance(2.0)  # Увеличение резкости (значение от 0 до 2)

        # Масштабирование изображения для увеличения разрешения
        new_size = (int(screenshot_pil.width * 2), int(screenshot_pil.height * 2))
        screenshot_pil = screenshot_pil.resize(new_size, Image.Resampling.LANCZOS)

        # Сохраняем с высоким качеством
        screenshot_pil.save(filename, quality=95, optimize=True)
        
        return {"status": "success", "file_path": os.path.abspath(filename)}
    except Exception as e:
        print(f"Ошибка создания скриншота: {str(e)}")
        return {"status": "error", "message": str(e)}

def preprocess_image(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Не удалось загрузить изображение: {image_path}")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite('processed_screenshot.png', gray)
        return gray
    except Exception as e:
        print(f"Ошибка предобработки изображения: {str(e)}")
        return None

def read_text_tesseract():
    try:
        result = make_screenshot()
        if result["status"] == "error":
            print(f"Ошибка: {result['message']}")
            return
        image_path = result["file_path"]
        
        # Предобработка изображения
        processed_image = preprocess_image(image_path)
        if processed_image is None:
            print("Не удалось обработать изображение.")
            return
        
        # Распознавание текста с оптимизированными параметрами
        text = pytesseract.image_to_string(processed_image, lang='rus+eng', config='--oem 1 --psm 6')
        print("Извлеченный текст (Pytesseract):")
        print(text if text.strip() else "Текст не распознан.")

    except Exception as e:
        print(f"Ошибка при распознавании текста: {str(e)}")

def read_text_easyocr():
    try:
        result = make_screenshot()
        if result["status"] == "error":
            print(f"Ошибка: {result['message']}")
            return
        
        print("Инициализация EasyOCR...")
        reader = easyocr.Reader(['ru', 'en'])
        result = reader.readtext('screenshot.png')
        print("Извлеченный текст (EasyOCR):")
        for detection in result:
            print(detection[1])  # detection[1] — извлеченный текст
    except Exception as e:
        print(f"Ошибка при распознавании текста: {str(e)}")

def read_text_paddleocr():
    try:
        result = make_screenshot()
        if result["status"] == "error":
            print(f"Ошибка: {result['message']}")
            return
        
        print("Инициализация PaddleOCR...")
        ocr = PaddleOCR(use_angle_cls=True, lang='ru')
        result = ocr.ocr('screenshot.png', cls=True)
        print("Извлеченный текст (PaddleOCR):")
        for line in result[0]:  # PaddleOCR возвращает список результатов
            print(line[1][0])  # Текст находится во втором элементе кортежа
    except Exception as e:
        print(f"Ошибка при распознавании текста: {str(e)}")

def print_play_text(model):
    print(f"Запуск {model} через 3 секунды...")
    time.sleep(3)
    print("Запуск.")

if __name__ == "__main__":
    while True:
        print("\n\n'1' - Pytesseract, '2' - EasyOCR, '3' - PaddleOCR, '4' - выйти.")
        command = input("Введите модель компьютерного зрения для проверки: ")

        if command == "1":
            print_play_text("Pytesseract")
            read_text_tesseract()
        elif command == "2":
            print_play_text("EasyOCR")
            read_text_easyocr()
        elif command == "3":
            print_play_text("PaddleOCR")
            read_text_paddleocr()
        elif command == "4":
            print("Выход.")
            break
        else:
            print("Неизвестная команда. Попробуйте снова.")