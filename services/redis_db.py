import os
import redis.asyncio as redis

# Constants for redis keys
MESSAGE_QUEUE = "message_queue"
MESSAGE_SET = "message_set"
LIVE_LOCATION = "state_live_location"
PINNED_LOCATION = "state_pinned_location"
NATURE = "state_nature"
LAST_REPONSE = "state_lastresponse"
PREVIOUS_QUEUE = "state_queue"


# API_KEY = os.getenv("REDIS_URL")
# if not API_KEY:
#     raise ValueError("Pinecode api_key not found")

redis_client = redis.Redis(
    decode_responses=True,
    host='localhost',
    port=6379
)
