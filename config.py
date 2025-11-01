import os

# Telegram Bot Configuration
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@NOTTYAPI")

# MongoDB Configuration
MONGO_DB_URI = os.getenv("MONGO_DB_URI", "")

# Security Configuration
SECRET_KEY_JWT = os.getenv("SECRET_KEY_JWT", "change-this-secret-key")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

# Application Configuration
CONCURRENCY_LIMIT = int(os.getenv("CONCURRENCY_LIMIT", "10"))
PORT = int(os.getenv("PORT", "8000"))
