import logging

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")


mongo_client: MongoClient | None = None
if settings.mongodb_url:
    try:
        mongo_client = MongoClient(settings.mongodb_url, serverSelectionTimeoutMS=5000)
        logger.info("MongoDB client configured for database '%s'", settings.mongodb_db_name)
    except Exception:
        logger.exception("MongoDB client initialization failed")
        mongo_client = None
else:
    logger.warning("MONGODB_URL is not set; MongoDB client is disabled")


def check_mongo_connection() -> bool:
    if mongo_client is None:
        logger.warning("MongoDB connection check skipped because MONGODB_URL is missing")
        return False

    try:
        mongo_client.admin.command("ping")
        logger.info("MongoDB connection successful")
        return True
    except PyMongoError:
        logger.exception("MongoDB connection failed")
        return False
