# inspect_memory.py
import chromadb

client = chromadb.PersistentClient(path="assistant_chroma_db") 

def inspect_memory():
    """Выводит ВСЕ записи в базе данных"""
    try:
        collection_name = "assistant_database"
        collection = client.get_collection(name=collection_name)
        print(f"Successfully connected to collection: '{collection_name}'")

    except Exception as e:
        print(f"Error connecting to collection: {e}")
        print("Available collections:", [col.name for col in client.list_collections()])
        exit()

    try:
        all_records = collection.get(
            include=["metadatas", "documents"]
        )

        num_records = len(all_records['ids'])
        print(f"\n--- Found {num_records} records in V.E.G.A. memory ---\n")

        for i in range(num_records):
            record_id = all_records['ids'][i]
            document = all_records['documents'][i]
            metadata = all_records['metadatas'][i]

            print(f"--- Record ID: {record_id} ---")
            print(f"Document (Text): {document}")
            print(f"Metadata: {metadata}")
            print("-" * 20 + "\n")

    except Exception as e:
        print(f"An error occurred while fetching records: {e}")


if __name__ == "__main__":
    inspect_memory()