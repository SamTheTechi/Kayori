import os
import redis.asyncio as redis

MESSAGE_QUEUE = "chatQueue"
MESSAGE_SET = "chatSet"
# API_KEY = os.getenv("REDIS_URL")
# if not API_KEY:
#     raise ValueError("Pinecode api_key not found")

redis_client = redis.Redis(
    decode_responses=True,
    host='localhost',
    port=6379
)
