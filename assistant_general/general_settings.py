# general_settings.py

from assistant_general.config import VEGA_PERSONALITY_CORE_ENGLISH, VEGA_PERSONALITY_CORE_RUSSIAN  # noqa: F401

# ДЛЯ database.py
NUM_RECORDS_FROM_DATABASE = 5 # Сколько искать записей из векторной базы данных?
SIMILARITY_THRESHOLD = 0.9 # Порог схожести для поиска записей в долговременной памяти (если схожесть записи менее чем это значение - запись пропускается)
# 0.80 - Для очень строгих записей
# 0.90 - Сбалансированно
# 1.00 - Для записей с некоторыми упущениями (возможными)

# ДЛЯ brain.py
MODEL_GEMINI = "gemini-flash-lite-latest" # gemini-2.5-flash or gemini-2.5-flash-lite or gemini-flash-latest or gemini-flash-lite-latest...
VEGA_PERSONALITY_CORE = VEGA_PERSONALITY_CORE_RUSSIAN # либо ENGLISH в конце, либо RUSSIAN
SHORT_TERM_MEMORY_PATH = "assistant_brain/short_term_memory.json"
MAX_MEMORY = 26 # Лимит кратковременной памяти

# ДЛЯ music_skills.py

FOOBAR_PATH = "C:\\Users\\ivanc\\Desktop\\Project_V.E.G.A\\VEGA_core\\assistant_music\\foobar2000\\foobar2000.exe"
MUSIC_LIBRARY_PATH = "C:\\Users\\ivanc\\Desktop\\Project_V.E.G.A\\VEGA_core\\assistant_music\\music"
SILENT_TRACK_PATH = "C:\\Users\\ivanc\\Desktop\\Project_V.E.G.A\\VEGA_core\\assistant_music\\music\\_silence.mp3"
