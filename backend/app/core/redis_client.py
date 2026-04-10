import logging

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

redis_client: Redis | None = None
if settings.redis_url:
	redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
	logger.info("Redis client configured")
else:
	logger.warning("REDIS_URL is not set; Redis cache fallback will be used")


def check_redis_connection() -> bool:
	if redis_client is None:
		logger.warning("Redis connection check skipped because REDIS_URL is missing")
		return False

	try:
		redis_client.ping()
		logger.info("Redis connection successful")
		return True
	except RedisError:
		logger.exception("Redis connection failed")
		return False
