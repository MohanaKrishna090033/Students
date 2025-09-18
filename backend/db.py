import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URL = os.getenv("mongodb+srv://admin:securepassword123@cluster0.dowqqtr.mongodb.net/emergentai?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.getenv("emergentai")

client = MongoClient(MONGO_URL)
db = client[DB_NAME]

print(f"✅ MongoDB Connected to database: {DB_NAME}")
