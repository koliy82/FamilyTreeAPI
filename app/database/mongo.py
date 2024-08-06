from pymongo import MongoClient

from app.config import MONGO_URL, MONGO_DATABASE

client = MongoClient(MONGO_URL)
db = client[MONGO_DATABASE]
braks = db["braks"]
users = db["users"]
