from datetime import datetime, timezone
from util.fixedQueue import FixedQueue

queue = FixedQueue(max_size=3)
natures = {
    "Affection": 0.5,
    "Amused": 0.2,
    "Inspired": 0.2,
    "Frustrated": 0.8,
    "Anxious": 0.2,
    "Curious": 0.2,
}

time_eclipse = {
    "time": 0,
}


def update_context(context: str):
    queue.enqueue(context)


def get_context():
    return queue.peek()


def update_last_time():
    time_eclipse["time"] = int(datetime.now(timezone.utc).timestamp())


def get_last_time() -> int:
    return int(datetime.now(timezone.utc).timestamp() - time_eclipse["time"])
