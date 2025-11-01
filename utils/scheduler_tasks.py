from database import mongo
from logging_ import LOGGER
from datetime import datetime
logger = LOGGER(__name__)

async def daily_reset_job():
    try:
        res = await mongo.mongodb.api_keys.update_many({}, {"$set": {"used_today": 0, "last_reset": datetime.utcnow()}})
        logger.info(f"Daily reset done. Modified: {res.modified_count}")
    except Exception as e:
        logger.error(f"Daily reset failed: {e}")
