import time
from util.agent_state import IDLE
from services.redis_db import (
    redis_client,
    LIVE_LOCATION,
    PINNED_LOCATION,
    LAST_REPONSE,
    NATURE,
    BOT_PRESENCE,
    BOT_LAST_ACTIVITY
)


# user's current location
async def set_live_location(latitude: float, longitude: float, timestamp: float):
    await redis_client.hset(LIVE_LOCATION, mapping={
        "latitude": latitude,
        "longitude": longitude,
    })


async def set_pinned_location():
    location = await redis_client.hgetall(LIVE_LOCATION)
    await redis_client.hset(PINNED_LOCATION, mapping={
        "latitude": location["latitude"],
        "longitude": location["longitude"],
    })


async def get_pinned_location():
    return await redis_client.hgetall(PINNED_LOCATION)


async def get_live_location():
    return await redis_client.hgetall(LIVE_LOCATION)


# kayori's mood level
async def set_mood(Affection: float, Amused: float, Inspired: float, Frustrated: float, Concerned: float, Curious: float):
    await redis_client.hset(NATURE, mapping={
        "Affection": Affection,
        "Amused": Amused,
        "Inspired": Inspired,
        "Frustrated": Frustrated,
        "Concerned": Concerned,
        "Curious": Curious,
    })


async def get_mood():
    return await redis_client.hgetall(NATURE)


# last time when user replied
async def set_last_response(time: str):
    await redis_client.hset(LAST_REPONSE, time)


async def get_last_response():
    return await redis_client.hgetall(LAST_REPONSE)


# init for all the values
async def init_location():
    pinned_exists = await redis_client.exists(PINNED_LOCATION)
    live_exists = await redis_client.exists(LIVE_LOCATION)

    if not pinned_exists:
        await redis_client.hset(PINNED_LOCATION, mapping={
            "latitude": 25.3436149,
            "longitude": 81.9102728,
            "timestamp": 0
        })

    if not live_exists:
        await redis_client.hset(LIVE_LOCATION, mapping={
            "latitude": 25.3436149,
            "longitude": 81.9102728,
            "timestamp": 0
        })


async def init_mood():
    exists = await redis_client.exists(NATURE)
    if not exists:
        await redis_client.hset(NATURE, mapping={
            "Affection": 0.0,
            "Amused": 0.0,
            "Inspired": 0.0,
            "Frustrated": 0.0,
            "Concerned": 0.0,
            "Curious": 0.0,
        })


async def init_last_response():
    exists = await redis_client.exists(LAST_REPONSE)
    if not exists:
        await redis_client.hset(LAST_REPONSE, mapping={
            "time": 0.0
        })


async def init_other_states():
    exists_presence = await redis_client.get(BOT_PRESENCE)
    if not exists_presence:
        await redis_client.set(BOT_PRESENCE, IDLE)
    exists_last_activitey = await redis_client.get(BOT_LAST_ACTIVITY)
    if not exists_last_activitey:
        await redis_client.set(BOT_LAST_ACTIVITY, str(time.time()))


async def init_states():
    await init_location()
    await init_mood()
    await init_last_response()
    await init_other_states()


# previous response context
# def update_context(context: str):
#     queue.enqueue(context)
#
#
# def get_context():
#     return queue.peek()
