from pymongo import MongoClient

from app.core.config import settings

MONGO_URL = "mongodb://localhost:27017"
DATABASE_NAME = "messages_db"
COLLECTION_NAME = "messages"  # название коллекции

def clear_messages_collection():
    client = MongoClient(MONGO_URL)
    db = client[DATABASE_NAME]

    if COLLECTION_NAME in db.list_collection_names():
        result = db[COLLECTION_NAME].delete_many({})
        print(f"Очищено документов в '{COLLECTION_NAME}': {result.deleted_count}")
    else:
        print(f"Коллекция '{COLLECTION_NAME}' не найдена.")

    print("Очистка завершена.")

if __name__ == "__main__":
    clear_messages_collection()
