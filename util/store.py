from datetime import datetime, timezone
from util.fixedQueue import FixedQueue

queue = FixedQueue(max_size=3)

location = {
    "latitude": 0,
    "longitude": 0,
    "timestamp": 0,
}

natures = {
    "Affection": 0.5,
    "Amused": 0.2,
    "Inspired": 0.2,
    "Frustrated": 0.8,
    "Anxious": 0.2,
    "Curious": 0.2,
}

last_response = {
    "time": 0,
}

current_pfp = {
    "img": "kaori1.webp"
}

# weather


def update_location(
    latitude: float,
    longitude: float,
    timestamp: float
):
    location["latitude"] = latitude
    location["longitude"] = longitude
    location["timestamp"] = timestamp


def update_context(context: str):
    queue.enqueue(context)


def update_pfp(img: str):
    current_pfp["img"] = img


def get_context():
    return queue.peek()


def update_last_time():
    last_response["time"] = int(datetime.now(timezone.utc).timestamp())


def get_last_time() -> int:
    return int((
        datetime.now(timezone.utc).timestamp() - last_response.get("time", 0)) / 60)
