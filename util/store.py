from util.fixedQueue import FixedQueue

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
