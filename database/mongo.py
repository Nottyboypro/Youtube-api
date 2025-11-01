from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI
from logging_ import LOGGER  # direct import – no relative issues

# Initialize logger
logger = LOGGER(__name__)

logger.info("Connecting to your Mongo Database...")

try:
    # Connect to MongoDB
    _mongo_async_ = AsyncIOMotorClient(MONGO_DB_URI)
    mongodb = _mongo_async_["Anon"]  # database name
    logger.info("✅ Connected to your Mongo Database.")
except Exception as e:
    logger.error(f"❌ Failed to connect to your Mongo Database: {e}")
    exit()
