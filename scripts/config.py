# scripts/config.py
import os
from dotenv import load_dotenv

# Load environment variables from secrets/.env
load_dotenv(dotenv_path="secrets/.env")

# Now retrieve environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_YOUTUBE_API_KEY")
MONGO_DB_URI = os.getenv("MONGO_DB_URI", "mongodb://localhost:27017/")

# Assistants
ASST_FOR_STORAGE = os.getenv("ASST_FOR_STORAGE", "asst_MdnotMzF8IO0gcdOUKMFqYiz")
ASST_FOR_WRITING = os.getenv("ASST_FOR_WRITING", "asst_WStvTCJsOGp9X2F4k8vUvIyo")














