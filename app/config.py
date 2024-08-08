import os

from dotenv import load_dotenv

print("123")
load_dotenv()

SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
MONGO_URL = os.getenv("MONGO_URI")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")
