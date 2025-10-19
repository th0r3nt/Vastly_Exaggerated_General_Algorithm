from assistant_general.config import VEGA_PERSONALITY_CORE_ENGLISH, VEGA_PERSONALITY_CORE_RUSSIAN
import logging

#### Для database.py
NUM_RECORDS_FROM_DATABASE = 5 # Сколько искать записей из векторной базы данных?
SIMILARITY_THRESHOLD = 1.05 # Порог схожести для поиска записей в долговременной памяти (0.0 - самые близкие знания, 1.0 - самые далекие)
# 0.80 - Для строгих записей (все записи, которые дальше, чем 0.75 - пропускаются)
# 0.90 - Сбалансированно
# 1.0 - Для записей с некоторыми возможными упущениями

#### Для logger_config.py
LOG_OUTPUT_LEVEL = logging.INFO # Какой уровень сообщений выводить в консоль: DEBUG, INFO, ERROR

#### Для brain.py
MODEL_GEMINI = "gemini-flash-latest" # gemini-2.5-flash or gemini-2.5-flash-lite or gemini-flash-latest or gemini-flash-lite-latest...
SHORT_TERM_MEMORY_PATH = "assistant_brain/short_term_memory.json"
MAX_MEMORY = 26 # Лимит кратковременной памяти
NUM_OF_NEWS_IN_BRIEFING = 8 # Количество новостей с Хабра, которые будут передаваться в утренний брифинг, чтобы Вега нашла самые интересные

VEGA_PERSONALITY_CORE = None

PERSONALITY_CORES = {
    "RUSSIAN": VEGA_PERSONALITY_CORE_RUSSIAN,
    "ENGLISH": VEGA_PERSONALITY_CORE_ENGLISH,
    # В будущем просто добавляем сюда: "GERMAN": VEGA_PERSONALITY_CORE_GERMAN,
}

def choose_language(language):
    global VEGA_PERSONALITY_CORE
    core = PERSONALITY_CORES.get(language) # .get() - безопасный способ получить значение
    if core:
        VEGA_PERSONALITY_CORE = core
        logging.debug(f"VEGA_PERSONALITY_CORE set for {language}")
    else:
        raise ValueError(f"Unsupported language: {language}")
    
####

# Настройки для утреннего брифинга
BRIEFING_START_HOUR = 6  # Брифинг можно проводить не раньше 6 утра

