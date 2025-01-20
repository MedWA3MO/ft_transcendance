import redis
import logging
from django.conf import settings

# Use the Redis URL provided by Render
redis_url = settings.REDIS_URL  # This will be set in your environment variables

# Initialize Redis connection
redis_conn = redis.StrictRedis.from_url(redis_url)

try:
    redis_conn.flushdb()
except redis.ConnectionError:
    logging.error("\nFailed to connect to Redis.\n")
