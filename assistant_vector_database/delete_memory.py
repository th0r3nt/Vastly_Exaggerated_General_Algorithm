import sys
import os
from datetime import datetime
import uuid
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_chroma import Chroma  

embedding_model = HuggingFaceEmbeddings(
    model_name = "BAAI/bge-m3", # Можно выбрать intfloat/multilingual-e5-large - она более быстрая, но менее точная
    encode_kwargs = {"normalize_embeddings": True} # при создании векторов из текста делать нормализацию
    ) 

# Векторная база данных
vectorstore = Chroma(
    collection_name="assistant_database", # Называем коллекцию внутри базы данных так
    embedding_function=embedding_model, # # Прикрепление модели эмбеддингов
    persist_directory="""./assistant_chroma_db""", # Сохранять в эту папку
    )


def delete_specific_records(ids_to_delete: str):
    """Удаляет записи из ChromaDB по списку их уникальных ID."""
    if not ids_to_delete:
        print("Список ID для удаления пуст. Ничего не сделано.")
        return

    print("Происходит удаление записей.")

    try:
        # Получаем записи, чтобы показать, что именно мы удаляем
        records_to_check = vectorstore.get(ids=ids_to_delete, include=["documents"])
        
        if not records_to_check['ids']:
            print("Ни одна из указанных записей не найдена в базе данных.")
            return

        print("\n--- Будет удалена следующая запись: ---")
        for i, doc_id in enumerate(records_to_check['ids']):
            doc_text = records_to_check['documents'][i]
            print(f"  - ID: {doc_id}")
            print(f"    Текст: {doc_text}")
        
        # Запрашиваем подтверждение
        confirm = input("\nВы уверены, что хотите продолжить? (y/n): \n>> ")
        if confirm.lower() != 'y':
            print("Удаление отменено.")
            return

        # Удаляем записи по их ID
        vectorstore.delete(ids=ids_to_delete)
        
        print(f"✅ Запись успешно удалена.")

    except Exception as e:
        print(f"\n❌ Произошла ошибка при удалении: {e}")

if __name__ == "__main__":
    print("Точные ID для удаления записей брать с помощью функции inspect_memory")
    while True:
        ids_to_delete = input("\nВведите точное ID записи для удаления: \n\n>> ")

        delete_specific_records(ids_to_delete)