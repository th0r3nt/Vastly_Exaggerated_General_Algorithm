# database.py
from assistant_tools.utils import play_sfx
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_chroma import Chroma  
from datetime import datetime
from assistant_event_bus.event_bus import subscribe, publish
import uuid
from assistant_general import general_settings as general_settings

# Эмбеддинг модель, чтобы превращать запросы пользователя в векторы и искать похожие в базе данных
print("Initialization of the embedding model.")
play_sfx("start_embedding_model")
embedding_model = HuggingFaceEmbeddings(
    model_name = "BAAI/bge-m3", # Можно выбрать intfloat/multilingual-e5-large - она более быстрая, но менее точная
    encode_kwargs = {"normalize_embeddings": True} # при создании векторов из текста делать нормализацию
    ) 

# Векторная база данных
print("Initialization of vector database.")
play_sfx("lauch_vector_database")
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

    results_with_scores = vectorstore.similarity_search_with_score(query, k=general_settings.NUM_RECORDS_FROM_DATABASE)

    # Если база пуста
    if not results_with_scores:
        result = {"original_query": query, "database_context": "No relevant records were found in the database."}
        print("No relevant records were found in the database.")
        publish("USER_SPEECH_AND_RECORDS_FOUND_IN_DB", result)
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

    result = {"original_query": query, "database_context": final_string}
    print(f"\nFound records in database for query '{query}': \n{final_string}")
    
    publish("USER_SPEECH_AND_RECORDS_FOUND_IN_DB", result)


def initialize_database():
    subscribe("USER_SPEECH", find_records_in_database)

