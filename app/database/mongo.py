from pymongo import MongoClient

from app.config import MONGO_URL

client = MongoClient(MONGO_URL)
db = client["test"]
braks = db["braks"]
