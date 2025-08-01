import os
from asyncio import Queue
from threading import Thread

import pika

USERNAME = os.environ['RABBITMQ_USER']
PASSWORD = os.environ['RABBITMQ_PASSWORD']
HOST = '192.168.1.142'
EXCHANGE = 'discord_atr'


class Subscriber:

    def __init__(self, bot, server_name, discord_server_id):

        self.server_name = server_name
        self.discord_server_id = discord_server_id
        self.bot = bot
        self.message_queue = Queue()

        credentials = pika.PlainCredentials(username=USERNAME, password=PASSWORD)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST, credentials=credentials))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue=server_name, exclusive=False, durable=False)
        self.queue_name = result.method.queue

        self.channel.queue_bind(exchange=EXCHANGE, queue=self.queue_name)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback, auto_ack=True)
        print(f" [*] Queue '{server_name}' Waiting for messages")

        self.thread = Thread(target=self.channel.start_consuming)
        self.thread.start()

    def callback(self, ch, method, properties, body):
        print(f" [*] Received message from queue {self.server_name}")
        self.message_queue.put(body)

    def close_queue(self):
        self.channel.stop_consuming()
        self.channel.queue_delete(self.queue_name)
        self.thread.join()

