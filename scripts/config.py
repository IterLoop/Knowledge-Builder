# scripts/config.py
import os
from dotenv import load_dotenv

# Load environment variables from secrets/.env
load_dotenv(dotenv_path="secrets/.env")

# Now retrieve environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_YOUTUBE_API_KEY")
MONGO_DB_URI = os.getenv("MONGO_DB_URI", "mongodb://localhost:27017/")
