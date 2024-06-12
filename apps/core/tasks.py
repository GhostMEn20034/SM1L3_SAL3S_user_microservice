import logging
from typing import Any
import dramatiq

from apps.core.message_broker.base.producer import Producer


@dramatiq.actor
def perform_data_topic_replication(exchange_name: str, routing_key: str, data: Any):
    """
    Performs replicating of the data to other "subscribed" microservices.
    """
    logging.info(routing_key)
    logging.info(str(data))

    producer = Producer(exchange_name=exchange_name, exchange_type='topic')
    producer.send_message(routing_key, data)
    producer.close()
