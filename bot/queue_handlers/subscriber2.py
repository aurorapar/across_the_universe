import asyncio
import functools
import logging
import json
import os
import ssl
import time
from enum import Enum

import pika
from pika.exceptions import AMQPConnectionError

from ..stoppable_thread import StoppableThread

logger = logging.getLogger(__name__)

USERNAME = os.environ['RABBITMQ_USER']
PASSWORD = os.environ['RABBITMQ_PASSWORD']
HOST = '192.168.1.142'
PORT = 5672
EXCHANGE = 'discord_atr'
EXCHANGE_TYPE = 'fanout'


def sync(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(f(*args, **kwargs))

    return wrapper


class Priority(Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 10


class BasicPikaClient:
    def __init__(self):
        self.username = USERNAME
        self.password = PASSWORD
        self.host = HOST
        self.port = PORT
        self.protocol = "amqp"

        self._init_connection_parameters()
        self._connect()

    def _connect(self):
        tries = 0
        while True:
            try:
                self.connection = pika.BlockingConnection(self.parameters)
                self.channel = self.connection.channel()
                if self.connection.is_open:
                    break
            except (AMQPConnectionError, Exception) as e:
                time.sleep(5)
                tries += 1
                if tries == 20:
                    raise AMQPConnectionError(e)

    def _init_connection_parameters(self):
        self.credentials = pika.PlainCredentials(self.username, self.password)
        self.parameters = pika.ConnectionParameters(
            self.host,
            int(self.port),
            "/",
            self.credentials,
        )
        if self.protocol == "amqps":
            # SSL Context for TLS configuration of Amazon MQ for RabbitMQ
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            ssl_context.set_ciphers("ECDHE+AESGCM:!ECDSA")
            self.parameters.ssl_options = pika.SSLOptions(context=ssl_context)

    def check_connection(self):
        if not self.connection or self.connection.is_closed:
            self._connect()

    def close(self):
        self.channel.close()
        self.connection.close()

    def declare_queue(
            self, queue_name, exclusive: bool = False, max_priority: int = 10
    ):
        self.check_connection()
        print(f"Trying to declare queue({queue_name})...")
        self.channel.queue_declare(
            queue=queue_name,
            exclusive=exclusive,
            arguments={"x-max-priority": max_priority},
        )

    def declare_exchange(self, exchange_name: str, exchange_type: str = "direct"):
        self.check_connection()
        self.channel.exchange_declare(
            exchange=exchange_name, exchange_type=exchange_type, durable=True
        )

    def bind_queue(self, exchange_name: str, queue_name: str, routing_key: str):
        self.check_connection()
        self.channel.queue_bind(
            exchange=exchange_name, queue=queue_name, routing_key=routing_key
        )

    def unbind_queue(self, exchange_name: str, queue_name: str, routing_key: str):
        self.channel.queue_unbind(
            queue=queue_name, exchange=exchange_name, routing_key=routing_key
        )


class BasicMessageReceiver(BasicPikaClient):
    def __init__(self):
        super().__init__()
        self.channel_tag = None

    def decode_message(self, body):
        return json.loads(body)

    def get_message(self, queue_name: str, auto_ack: bool = False):
        method_frame, header_frame, body = self.channel.basic_get(
            queue=queue_name, auto_ack=auto_ack
        )
        if method_frame:
            print(f"{method_frame}, {header_frame}, {body}")
            return method_frame, header_frame, body
        else:
            print("No message returned")
            return None

    def consume_messages(self, queue, callback):
        self.check_connection()
        self.channel_tag = self.channel.basic_consume(
            queue=queue, on_message_callback=callback, auto_ack=True
        )
        print(" [*] Waiting for messages. To exit press CTRL+C")
        self.channel.start_consuming()

    def cancel_consumer(self):
        if self.channel_tag is not None:
            self.channel.basic_cancel(self.channel_tag)
            self.channel_tag = None
        else:
            logger.error("Do not cancel a non-existing job")


class MyConsumer(BasicMessageReceiver):

    def __init__(self, bot, discord_server_name, discord_server_id, discord_channel_id):
        super().__init__()
        self.bot = bot
        self.discord_server_name = discord_server_name
        self.discord_server_id = discord_server_id
        self.discord_channel_id = discord_channel_id

    @sync
    async def consume(self, channel, method, properties, body):
        original_message = self.decode_message(body=body)
        for guild in self.bot.guilds:
            discord_channel = guild.get_channel(self.discord_channel_id)
            await discord_channel.send(
               f"{original_message["user_account"]}/"
               f"{original_message["user_name"]} from "
               f"{original_message["source_server"]}#{original_message["source_channel"]}"
               f" at {time.ctime(original_message["time"])} said:\n{original_message["message"]}"
            )


def create_consumer(bot, server_name, discord_channel_id, discord_server_id):
    worker = MyConsumer(bot, server_name, discord_server_id, discord_channel_id)
    worker.declare_queue(queue_name=worker.discord_server_name)
    worker.declare_exchange(exchange_name=EXCHANGE, exchange_type=EXCHANGE_TYPE)
    worker.bind_queue(exchange_name=EXCHANGE, queue_name=worker.discord_server_name, routing_key='')
    worker_thread = StoppableThread(target=worker.consume_messages, kwargs={
        'queue': server_name,
        'callback': worker.consume}
    )
    return worker_thread
