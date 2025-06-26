import os
import redis.asyncio as redis

# Constants for redis keys
MESSAGE_QUEUE = "message_queue"
MESSAGE_SET = "message_set"
LOCATION = "state_location"
NATURE = "state_nature"
LAST_REPONSE = "state_lastresponse"
CURRENT_PFP = "state_pfp"
PREVIOUS_QUEUE = "state_queue"


# API_KEY = os.getenv("REDIS_URL")
# if not API_KEY:
#     raise ValueError("Pinecode api_key not found")

redis_client = redis.Redis(
    decode_responses=True,
    host='localhost',
    port=6379
)
