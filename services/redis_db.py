import redis.asyncio as redis

QUEUE = "chatQueue"

redis_client = redis.Redis(
    decode_responses=True,
    host='localhost',
    port=6379
)
