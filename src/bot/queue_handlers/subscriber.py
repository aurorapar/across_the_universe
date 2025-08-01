import os
from queue import Queue
from threading import Thread

from amqpstorm import Connection

USERNAME = os.environ['RABBITMQ_USER']
PASSWORD = os.environ['RABBITMQ_PASSWORD']
HOST = '192.168.1.142'
EXCHANGE = 'discord_atr'


class Subscriber:

    def __init__(self, bot, server_name, discord_server_id):
        self.server_name = server_name
        self.discord_server_id = discord_server_id
        self.bot = bot
        self.queue = None
        self.message_queue = Queue()

        self.thread = Thread(target=self._start)
        self.thread.start()

    def _start(self):
        with Connection(HOST, USERNAME, PASSWORD) as connection:
            with connection.channel() as channel:
                self.queue = channel.queue
                self.queue.declare(self.server_name, auto_delete=True)
                self.queue.bind(queue=self.server_name, exchange=EXCHANGE)
                channel.basic.consume(self.on_message, self.server_name, no_ack=False)

                try:
                    # Start consuming messages.
                    channel.start_consuming()
                except KeyboardInterrupt:
                    channel.close()

    def on_message(self, message):
        self.message_queue.put(message.body)
        message.ack()

