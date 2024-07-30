from django.conf import settings

from .base_queue_listenter import BaseQueueListener
from services.orders.message_handler import handle_message

class OrderProcessingQueueListener(BaseQueueListener):
    BINDING_KEY = 'orders.#'
    exchange_name = settings.ORDER_PROCESSING_EXCHANGE_TOPIC_NAME
    message_handler_func = staticmethod(handle_message)
