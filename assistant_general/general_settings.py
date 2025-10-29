from assistant_general.config import VEGA_PERSONALITY_CORE_ENGLISH, VEGA_PERSONALITY_CORE_RUSSIAN
import logging


# Настройки для: database.py
# -----------------------------------------------
# ЭКСПЕРИМЕНТАЛЬНЫЕ НАСТРОЙКИ: можно указать большое число в NUM_RECORDS_FROM_DATABASE (например, 50) и указать 1.5 в SIMILARITY_THRESHOLD, чтобы передавать большинство записей для нейросети
# Это может увеличить контекст нейросети, но может также увеличить задержку

NUM_RECORDS_FROM_DATABASE = 30 # Сколько искать записей из векторной базы данных?
SIMILARITY_THRESHOLD = 1.4 # Порог схожести для поиска записей в долговременной памяти (0.0 - только близкие знания, 2.0 - только самые далекие и несвязанные)
# 0.80 - Для строгих записей (все записи, которые дальше, чем 0.75 - пропускаются)
# 0.90 - Сбалансированно
# 1.0 - Для записей с некоторыми возможными упущениями
# -----------------------------------------------



# Настройки для: logger_config.py
# -----------------------------------------------
LOG_OUTPUT_LEVEL = logging.INFO # Какой уровень сообщений выводить в консоль: DEBUG, INFO, ERROR
# -----------------------------------------------

# Настройки для: logger_config.py
# -----------------------------------------------
CHROMA_COLLECTION_NAME = "assistant_database"
# -----------------------------------------------

# Настройки для: brain.py
# -----------------------------------------------
MODEL_GEMINI = "gemini-flash-latest" # gemini-2.5-flash or gemini-2.5-flash-lite or gemini-flash-latest or gemini-flash-lite-latest...
MAX_MEMORY = 26 # Лимит кратковременной памяти
NUM_OF_NEWS_IN_BRIEFING = 10 # Количество новостей с Хабра, которые будут передаваться в утренний брифинг, чтобы Вега нашла самые интересные
BRIEFING_START_HOUR = 6  # Брифинг можно проводить не раньше 6 утра
TASKS_COMPLETED_FILE_PATH = "assistant_background_tasks/tasks_completed_today.json"

SHORT_TERM_MEMORY_PATH = "assistant_brain/short_term_memory.json"
ALL_HISTORY_OF_DIALOGUES_PATH = "assistant_brain/all_history_of_dialogues.json"

VEGA_PERSONALITY_CORE = None
PERSONALITY_CORES = {"RUSSIAN": VEGA_PERSONALITY_CORE_RUSSIAN, "ENGLISH": VEGA_PERSONALITY_CORE_ENGLISH,}
def choose_language(language):
    """Вызывается из main.py, передается язык: на его основе передается либо английский промпт, либо русский"""
    global VEGA_PERSONALITY_CORE
    core = PERSONALITY_CORES.get(language) # .get() - безопасный способ получить значение
    if core:
        VEGA_PERSONALITY_CORE = core
        logging.debug(f"VEGA_PERSONALITY_CORE set for {language}")
    else:
        raise ValueError(f"Unsupported language: {language}")
# -----------------------------------------------


