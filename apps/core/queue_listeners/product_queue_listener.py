from django.conf import settings

from .base_queue_listenter import BaseQueueListener
from services.products.message_handler import handle_message

class ProductQueueListener(BaseQueueListener):
    BINDING_KEY = 'products.#'
    exchange_name = settings.PRODUCT_CRUD_EXCHANGE_TOPIC_NAME
    message_handler_func = staticmethod(handle_message)
