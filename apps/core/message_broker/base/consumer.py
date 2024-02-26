from typing import Callable

from pika import URLParameters, BlockingConnection

from django.conf import settings
from pika.adapters.blocking_connection import BlockingChannel


class Consumer:
    """
    Class responsible for getting messages from the broker
    """
    def __init__(self, exchange_name: str, exchange_type: str):
        self._exchange_name: str = exchange_name

        self._parameters: URLParameters = URLParameters(settings.AMPQ_CONNECTION_URL)
        self._connection: BlockingConnection = BlockingConnection(parameters=self._parameters)
        self._channel: BlockingChannel = self._connection.channel()

        self._channel.exchange_declare(exchange=self._exchange_name, exchange_type=exchange_type)

        result = self._channel.queue_declare('', exclusive=True)
        self._queue_name: str = result.method.queue

    def bind_queue(self, binding_key: str):
        self._channel.queue_bind(exchange=self._exchange_name, queue=self._queue_name, routing_key=binding_key)

    def consume(self, callback: Callable, auto_ack: bool = True):
        self._channel.basic_consume(queue=self._queue_name, on_message_callback=callback, auto_ack=auto_ack)
        self._channel.start_consuming()
