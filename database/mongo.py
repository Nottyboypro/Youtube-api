import logging
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI

# Setup simple logger
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("MongoDB")

logger.info("Connecting to your Mongo Database...")

try:
    _mongo_async_ = AsyncIOMotorClient(MONGO_DB_URI)
    mongodb = _mongo_async_["Anon"]  # Database name 'Anon'
    logger.info("✅ Connected to your Mongo Database.")
except Exception as e:
    logger.error(f"❌ Failed to connect to your Mongo Database: {e}")
    exit()
