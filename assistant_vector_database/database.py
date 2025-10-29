# database.py
from assistant_tools.utils import play_sfx
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_chroma import Chroma  
from datetime import datetime
from assistant_event_bus.event_bus import subscribe, publish
import uuid
from assistant_general import general_settings as general_settings
from assistant_event_bus import event_definitions as events
import os
from dotenv import load_dotenv
import chromadb

load_dotenv() # для загрузки API ключей и путей из .env
LOCAL_EMBEDDING_MODEL_PATH = os.getenv("LOCAL_EMBEDDING_MODEL_PATH")

# Эмбеддинг модель, чтобы превращать запросы пользователя в векторы и искать похожие в базе данных
print("Initialization of the embedding model.")
play_sfx("start_additional_system")
embedding_model = HuggingFaceEmbeddings(
    model_name=LOCAL_EMBEDDING_MODEL_PATH,
    encode_kwargs={"normalize_embeddings": True}
)

# Векторная база данных
print("Initialization of vector database.")
play_sfx("start_additional_system")
vectorstore = Chroma(
    collection_name=general_settings.CHROMA_COLLECTION_NAME, # Называем коллекцию внутри базы данных так
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

    play_sfx('silent_execution')
    print(f"New entry added to memory: '{new_text}'")

def find_records_in_database(**kwargs):
    """Ищет записи в векторной базе данных и форматирует результат в читаемую строку."""

    query = kwargs.get('query')
    if not query:
        play_sfx('silent_error')
        return
    
    play_sfx('search')
    print("Поиск записей в базе данных.")
    results_with_scores = vectorstore.similarity_search_with_score(query, k=general_settings.NUM_RECORDS_FROM_DATABASE)

    # Если база пуста
    if not results_with_scores:
        result = {"original_query": query, "database_context": "No relevant records were found in the database."}
        print("No relevant records were found in the database.")
        publish(events.USER_SPEECH_AND_RECORDS_FOUND_IN_DB, result)
        return 
    
    formatted_lines = []

    print("\nSearching for records in the database:")

    for document, score in results_with_scores:
        if score <= general_settings.SIMILARITY_THRESHOLD:
            # Если запись ДОСТАТОЧНО похожа, обрабатываем ее
            print(f"Record is relevant enough (score: {score:.2f}, threshold: {general_settings.SIMILARITY_THRESHOLD})")
            
            date = document.metadata.get('creation_date', 'Date not found')
            text = document.page_content
            
            # Добавим оценку в вывод для наглядности
            formatted_lines.append(f"[Score: {score:.2f}] {date}: {text}")
        else:
            # Если запись НЕдостаточно похожа, мы можем ее проигнорировать
            print(f"Record is NOT relevant enough (score: {score:.2f}, threshold: {general_settings.SIMILARITY_THRESHOLD}). Skipping.")
            # Мы можем либо ничего не делать, либо добавить сообщение об этом
            # formatted_lines.append(f"[Not relevant enough, score: {score:.2f}]") 

    # Если после фильтрации не осталось релевантных записей
    if not formatted_lines:
        final_string = "Found some records, but none were similar enough to the query."
    else:
        # Соединяем только релевантные строки
        final_string = "\n".join(formatted_lines)

    play_sfx('silent_execution')
    result = {"original_query": query, "database_context": final_string}
    if general_settings.NUM_RECORDS_FROM_DATABASE <= 15: # Если передана вся база - консоль будет вся в записях; стоит сделать проверку
        print(f"\nFound records in database for query '{query}': \n{final_string}")
    
    publish(events.USER_SPEECH_AND_RECORDS_FOUND_IN_DB, result)

def get_all_records_as_string():
    """Извлекает все записи из ChromaDB и форматирует их в единую строку."""
    try:
        client = chromadb.PersistentClient(path="./assistant_chroma_db")
        collection = client.get_collection(name=general_settings.CHROMA_COLLECTION_NAME)
        
        all_records = collection.get(include=["metadatas", "documents"])
        
        if not all_records['ids']:
            return "База данных (память) пуста."
        
        formatted_lines = []
        for i in range(len(all_records['ids'])):
            doc = all_records['documents'][i]
            meta = all_records['metadatas'][i]
            date = meta.get('creation_date', 'N/A')
            formatted_lines.append(f"[{date}]: {doc}")
        
        return "\n".join(formatted_lines)
    except Exception as e:
        print(f"Ошибка при получении всех записей из БД: {e}")
        return f"Ошибка при доступе к памяти: {e}"


def initialize_database():
    subscribe(events.USER_SPEECH, find_records_in_database)

if __name__ == "__main__":
    while True:
        new_record = input("Введите новую запись, которую нужно добавить (введите '0' для выхода): \n>>")

        if new_record != "0":
            add_new_memory(new_record)
        else:
            break
