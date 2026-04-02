import os

from pymongo import MongoClient


def get_mongo_client() -> MongoClient:
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    return MongoClient(mongo_url)


def get_products_collection():
    client = get_mongo_client()
    db_name = os.getenv("MONGO_DB", "inventory")
    collection_name = os.getenv("MONGO_COLLECTION", "products")
    return client[db_name][collection_name]

