import wmi
from datetime import datetime
import logging
import sys
import os
import requests
from datetime import datetime  # noqa: F811

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from assistant_general.logger_config import setup_logger  # noqa: E402

setup_logger()
logger = logging.getLogger(__name__)

# ЧТО НУЖНО РЕАЛИЗОВАТЬ:
# Задачи, выполняемые только ОДИН раз в день 
# "morning_briefing": - ежедневный брифинг с погодой, новыми новостями
# "file_cleanup": - очистка ненужный файлов каждый вечер-ночь
# "system_health_check": - проверка логов нагрузки системы каждый вечер
# "social_digest": - парсит соцсети (например, телеграм-канал) и выдает краткую сводку самых важных новостей от контактов или каналов    

# Задачи, выполняемые ЧАЩЕ раза в день
# "arxiv_parse": - парсинг научных статей каждые 6 часов.
# "system_monitor_snapshot": Сохранение "снимка" состояния системы (CPU, RAM) каждые 5 минут для построения исторических графиков (обязательно для system_health_check)



