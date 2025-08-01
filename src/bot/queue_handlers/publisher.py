import json
import os
from queue import Queue
from threading import Thread

from amqpstorm import Connection
from amqpstorm import Message

USERNAME = os.environ['RABBITMQ_USER']
PASSWORD = os.environ['RABBITMQ_PASSWORD']
HOST = '192.168.1.142'
EXCHANGE = 'discord_atr'


class Publisher:

    def __init__(self):
        self.message_queue = Queue()

        self.thread = Thread(target=self._start)
        self.thread.start()

    def _start(self):

        with Connection(HOST, USERNAME, PASSWORD) as connection:
            with connection.channel() as channel:
                # Declare the Queue, 'simple_queue'.

                while True:
                    if not self.message_queue.empty():
                        message = Message.create(channel, self.message_queue.get())
                        self.message_queue.task_done()
                        message.publish(EXCHANGE)

    def send_message(self, message):
        print(" [*] Trying to put message into Queue")
        self.message_queue.put(json.dumps(message))
