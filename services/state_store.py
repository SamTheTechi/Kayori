from util.fixedQueue import FixedQueue
from services.redis_db import (
    redis_client,
    LOCATION,
    LAST_REPONSE,
    NATURE,
    CURRENT_PFP,
    PREVIOUS_QUEUE
)


queue = FixedQueue(max_size=3)

location = {
    "latitude": 0,
    "longitude": 0,
    "timestamp": 0,
}

natures = {
    "Affection": 0,
    "Amused": 0,
    "Inspired": 0,
    "Frustrated": 0,
    "Concerned": 0,
    "Curious": 0,
}

last_response = {
    "time": 0,
}

current_pfp = {
    "img": "kaori1.webp"
}


async def set_location(
    latitude: float,
    longitude: float,
    timestamp: float
):
    await redis_client.hset(LOCATION, mapping={
        "latitude": latitude,
        "longitude": longitude,
        "timestamp":  timestamp
    })


async def get_location():
    return await redis_client.hgetall(LOCATION)


async def set_nature(
    Affection: float,
    Amused: float,
    Inspired: float,
    Frustrated: float,
    Concerned: float,
    Curious: float,
):
    await redis_client.hset(NATURE, mapping={
        "Affection": Affection,
        "Amused": Amused,
        "Inspired": Inspired,
        "Frustrated": Frustrated,
        "Concerned": Concerned,
        "Curious": Curious,
    })


async def get_nature():
    return await redis_client.hgetall(NATURE)


def update_context(context: str):
    queue.enqueue(context)


def update_pfp(img: str):
    current_pfp["img"] = img


def get_context():
    return queue.peek()
