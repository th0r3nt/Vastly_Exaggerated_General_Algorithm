# logger_config.py
import logging
import sys
from assistant_general.general_settings import LOG_OUTPUT_LEVEL

# Чтобы инициализировать логгер в других файлах:
# import logging
# from assistant_general.logger_config import setup_logger
# setup_logger()
# logger = logging.getLogger(__name__)
# logger.info("Test")

def setup_logger():
    """Настраивает корневой логгер, от которого наследуются все остальные."""
    
    # Получаем корневой логгер, передав пустое имя
    root_logger = logging.getLogger()
    
    if root_logger.hasHandlers():
        return

    root_logger.setLevel(LOG_OUTPUT_LEVEL)

    # Создаем обработчики
    stdout_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler('VEGA.log', mode='a', encoding='utf-8')

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
    )

    # Применяем форматтер к обработчикам
    stdout_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Добавляем обработчики к корневому логгеру
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(file_handler)

