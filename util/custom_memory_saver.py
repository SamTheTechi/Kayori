from langgraph.checkpoint.memory import InMemorySaver


class CustomMemorySaver(InMemorySaver):
    """
    this method is implemented to all the recent memory when kayori wents to sleep
    """

    def clear_all(self):
        for thread_id in list(self.storage.keys()):
            self.delete_thread(thread_id)
