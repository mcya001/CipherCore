import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB = os.getenv("MYSQL_DB")
    MYSQL_CURSORCLASS = "DictCursor"
    # Use environment variable for secret key, or generate a fixed one for development
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production-2024")