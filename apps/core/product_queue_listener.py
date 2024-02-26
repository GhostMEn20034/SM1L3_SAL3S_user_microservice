import json
import threading
import logging
from django.conf import settings

from services.products.message_handler import handle_message
from .message_broker.base.consumer import Consumer

BINDING_KEY = 'products.#'

class ProductQueueListener(threading.Thread):
    def __init__(self):
        super().__init__()
        self.consumer = Consumer(
            exchange_name=settings.PRODUCT_CRUD_EXCHANGE_TOPIC_NAME,
            exchange_type="topic"
        )
        self.consumer.bind_queue(BINDING_KEY)

    def callback(self, ch, method, properties, body):
        print(f" [x] {method.routing_key}:{json.loads(body)}")
        handle_message(method.routing_key, json.loads(body))

    def run(self):
        logging.info('Listener was launched')
        self.consumer.consume(callback=self.callback)
