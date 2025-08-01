import json
import os
from queue import Queue
from threading import Thread

import pika
from pika.credentials import PlainCredentials

USERNAME = os.environ['RABBITMQ_USER']
PASSWORD = os.environ['RABBITMQ_PASSWORD']
HOST = '192.168.1.142'
EXCHANGE = 'discord_atr'


class Publisher:

    def __init__(self):

        self.message_queue = Queue()
        credentials = PlainCredentials(USERNAME, PASSWORD)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST, credentials=credentials))
        self.channel = self.connection.channel()

        def publish_messages():
            while True:
                message = self.message_queue.get()
                print(f" [*] Trying to put message into exchange")
                self.channel.basic_publish(exchange=EXCHANGE, routing_key='', body=message)
                print(f" [*] Marking queue as task done")
                self.message_queue.task_done()

        message_publisher = Thread(target=publish_messages)
        message_publisher.daemon = True
        message_publisher.start()

        print(" [*] Publisher ready")

    def send_message(self, message):
        print(" [*] Trying to put message into Queue")
        self.message_queue.put(json.dumps(message))
