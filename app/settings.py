# app/settings.py
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")
DATABASE_URL = os.getenv("DATABASE_URL")

# Bot behavior
RATE_LIMIT_SECONDS = int(os.getenv("RATE_LIMIT_SECONDS", "120"))  # seconds between comments per user
PROFANITY_WORDS = (os.getenv("PROFANITY_WORDS") or "badword1,badword2").split(",")
TARGETS = {"A": "Person A", "B": "Person B", "C": "Person C"}

# Ensure required environment variables are set
if not all([BOT_TOKEN, GROUP_CHAT_ID, DATABASE_URL]):
    raise ValueError("Missing required environment variables: BOT_TOKEN, GROUP_CHAT_ID, DATABASE_URL")

# Convert GROUP_CHAT_ID to integer
try:
    GROUP_CHAT_ID = int(GROUP_CHAT_ID)
except (ValueError, TypeError):
    raise ValueError("GROUP_CHAT_ID must be a valid integer.")
