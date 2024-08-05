import os

from dotenv import load_dotenv

print("123")
load_dotenv()

MONGO_URL = os.getenv("MONGO_URI")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")
