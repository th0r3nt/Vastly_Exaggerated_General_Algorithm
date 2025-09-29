# database.py

from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_chroma import Chroma  
from datetime import datetime
from assistant_event_bus.event_bus import subscribe, publish
import uuid

# Эмбеддинг модель, чтобы превращать запросы пользователя в векторы и искать похожие в базе данных
print("Initialization of the embedding model.")
embedding_model = HuggingFaceEmbeddings(
    model_name = "BAAI/bge-m3", # Можно выбрать intfloat/multilingual-e5-large - она более быстрая, но менее точная
    encode_kwargs = {"normalize_embeddings": True} # при создании векторов из текста делать нормализацию
    ) 

# Векторная база данных
print("Initialization of vector database.")
vectorstore = Chroma(
    collection_name="assistant_database", # Называем коллекцию внутри базы данных так
    embedding_function=embedding_model, # # Прикрепление модели эмбеддингов
    persist_directory="""./assistant_chroma_db""", # Сохранять в эту папку
    )

def add_new_memory(new_text: str):
    """Принимает текст, генерирует для него уникальный ID, добавляет текущую дату в метаданные и сохраняет в Chroma."""
    current_date = datetime.now().strftime("%d.%m.%Y")
    record_id = str(uuid.uuid4()) # Генерируем уникальный ID для записи
    
    metadata = {"creation_date": current_date}

    # Добавляем текст, его ID и его метаданные в базу.
    # Важно: add_texts принимает списки, поэтому оборачиваем все в []
    vectorstore.add_texts(
        texts=[new_text], 
        ids=[record_id], 
        metadatas=[metadata]
    )
    
    print(f"New entry added to memory: '{new_text}'")

def find_records_in_database(**kwargs):
    """Ищет записи в векторной базе данных и форматирует результат в читаемую строку."""

    # Если запрос пуст
    query = kwargs.get('query')
    if not query:
        return

    result_DB = vectorstore.similarity_search(query, k=5)

    # Если база пуста
    if not result_DB:
        result = {"original_query": query, "database_context": "No relevant records were found in the database."}
        print("No relevant records were found in the database.")
        publish("USER_SPEECH_AND_RECORDS_FOUND_IN_DB", result)
        return 

    formatted_lines = []
    
    for document in result_DB:
        # Извлекаем дату (которая у вас является ID) из метаданных

        date = document.metadata.get('creation_date', 'Date not found') # Используем .get(), чтобы избежать ошибки, если вдруг 'id' не найдется
        
        # Извлекаем текст записи
        text = document.page_content
        
        formatted_lines.append(f"{date}: {text}")

    # Выводим красивый, отформатированный результат
    final_string = "\n".join(formatted_lines)

    result = {"original_query": query, "database_context": final_string}
    print(f"Found records in database: \n{final_string}")
    
    publish("USER_SPEECH_AND_RECORDS_FOUND_IN_DB", result)


def initialize_database():
    subscribe("USER_SPEECH", find_records_in_database)











