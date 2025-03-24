from collections import deque


class FixedQueue:
    def __init__(self, max_size: int):
        self.queue = deque(maxlen=max_size)

    def enqueue(self, context: str):
        self.queue.appendleft(context)

    def peek(self) -> list:
        return list(self.queue)
