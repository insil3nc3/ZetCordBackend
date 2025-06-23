from pymongo import MongoClient
from app.core.config import settings
import pprint

# ========== Константы ==========
# URL для подключения к MongoDB и имя базы данных
MONGO_URL = "mongodb://localhost:27017"
DATABASE_NAME = "messages_db"


# ==============================

def clear_collections():
    # ========== Подключение к MongoDB ==========
    # Создание клиента MongoDB и подключение к базе данных
    client = MongoClient(MONGO_URL)
    db = client[DATABASE_NAME]
    # ==============================

    # ========== Получение списка коллекций ==========
    # Получение имен всех коллекций в базе данных
    collections = db.list_collection_names()
    print(f"Найдено коллекций: {collections}")
    # ==============================

    # ========== Вывод документов ==========
    # Перебор всех коллекций и вывод их содержимого
    for name in collections:
        print(f"\nКоллекция: {name}")
        collection = db[name]
        # Получение всех документов в коллекции
        documents = collection.find()
        document_count = collection.count_documents({})
        doc = collection.find_one()

        if document_count == 0:
            print("  Документы: отсутствуют")
        else:
            print(f"  Документы (всего: {document_count}):")
            # Вывод каждого документа с отступами для читаемости
            for doc in documents:
                pprint.pprint(doc, indent=2)
    # ==============================

    # ========== Закрытие соединения ==========
    # Закрытие клиента MongoDB
    client.close()
    print("\nВсе коллекции и их документы выведены.")
    # ==============================


if __name__ == "__main__":
    clear_collections()