from datetime import datetime
import uuid
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_chroma import Chroma  
import assistant_general.general_settings as general_settings

# Эмбеддинг модель, чтобы превращать запросы пользователя в векторы и искать похожие в базе данных
embedding_model = HuggingFaceEmbeddings(
    model_name = "BAAI/bge-m3", # Можно выбрать intfloat/multilingual-e5-large - она более быстрая, но менее точная
    encode_kwargs = {"normalize_embeddings": True} # при создании векторов из текста делать нормализацию
    ) 

# Векторная база данных
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
    
    print(f"New entry added to memory: '{new_text}'")

if __name__ == "__main__":
    while True:
        new_record = input("\nВведите новую запись, которую нужно добавить (введите '0' для выхода): \n>> ")

        if new_record != "0":
            add_new_memory(new_record)
        else:
            break