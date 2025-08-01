import threading


class StoppableThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscriber_worker = kwargs['worker']

    def stop(self):
        self.subscriber_worker.stop_consuming()
        self.subscriber_worker.queue_unbind(self.subscriber_worker.discord_server_name)
        self.subscriber_worker.queue_purge(self.subscriber_worker.discord_server_name)
        self.subscriber_worker.queue_delete(self.subscriber_worker.discord_server_name)
        self.subscriber_worker.close()
        self.join()
