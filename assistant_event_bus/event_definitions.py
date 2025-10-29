"""
Центральный реестр всех типов событий, используемых в системе V.E.G.A.
Импортировать эти константы вместо использования "магических строк",
чтобы избежать опечаток и сделать код более читаемым.
"""

USER_SPEECH = "USER_SPEECH"  # Опубликовано, когда пользователь что-то сказал/написал. kwargs: {'query': str}
USER_SPEECH_AND_RECORDS_FOUND_IN_DB = "USER_SPEECH_AND_RECORDS_FOUND_IN_DB" # Опубликовано после поиска в БД. kwargs: {'original_query': str, 'database_context': str}
GEMINI_RESPONSE = "GEMINI_RESPONSE"  # Опубликовано, когда Gemini сгенерировал финальный ответ. kwargs: {'text': str}
HOTKEY_ANALYSIS_TRIGGERED = "HOTKEY_ANALYSIS_TRIGGERED"
