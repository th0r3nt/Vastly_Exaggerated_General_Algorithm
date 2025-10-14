import wmi
from datetime import datetime
import logging
import sys
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime  # noqa: F811

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from assistant_general.logger_config import setup_logger  # noqa: E402

setup_logger()
logger = logging.getLogger(__name__)

def get_system_metrics():
    """Возвращает текущую нагрузку процессора, видеокарты и оперативной памяти один раз."""
    try:
        w = wmi.WMI(namespace="root\OpenHardwareMonitor")
        sensors = w.Sensor()
        if not sensors:
            return "No sensors are available. OpenHardwareMonitor may not be running."

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
        output = (
            f"Readings from the main PC sensors ({now.strftime('%H:%M:%S')}): \nCPU: {cpu_temp}, {cpu_load}; \nGPU: {gpu_temp}, {gpu_load}; \nRAM: {ram_load}"
        )
        return output
    
    except Exception as e:
        return f"Error: {str(e)}. Make sure OpenHardwareMonitor is running."

# def network_monitor(): # TODO: НЕ РАБОТАЕТ КОРРЕКТНО, ИСПРАВИТЬ
#     try:
#         # Используем secure=True, как у вас было
#         st = speedtest.Speedtest(secure=True)
        
#         print("Getting servers...")
#         st.get_servers()

#         print("Testing download speed...")
#         # Исправил деление на 1,000,000 для корректных Мбит/с
#         download_speed = st.download() / 1_000_000
        
#         print("Testing upload speed...")
#         upload_speed = st.upload() / 1_000_000
        
#         # Пинг будет измерен во время тестов скачивания/отдачи
#         ping_result = st.results.ping

#         print("-" * 30)
#         print("Current internet speed:")
#         print(f"  Download Speed: {download_speed:.2f} Mbps")
#         print(f"  Upload Speed: {upload_speed:.2f} Mbps")
#         print(f"  Ping: {ping_result:.2f} ms")
#         print("-" * 30)
    
#     except Exception as e:
#         print(f"Error during network monitoring: {e}")


def get_habr_news(limit=5):
    """Получает топ статей с Habr.com."""
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

        for i, art in enumerate(result, 1):
            print(f"{i}. {art['title']} \nСсылка: {art['link']} \nКратко: {art['summary']}\n")
    
        return f"{i}. {art['title']} \nАвтор: {art['author']} \nДата: {art['pub_date']} \nСсылка: {art['link']} \nКратко: {art['summary']}\n"
    
    except requests.RequestException as e:
        print(f"Error requesting page: {e}")
        return []
    except Exception as e:
        print(f"Parsing error: {e}")
        return []

# Пример использования
if __name__ == "__main__":
    get_habr_news()
