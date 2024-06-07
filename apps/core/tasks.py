import logging
from typing import Any

import dramatiq


@dramatiq.actor
def perform_data_replication(routing_key: str, data: Any):
    """
    Performs replicating of the data to other "subscribed" microservices.
    """
    logging.info(routing_key)
    logging.info(str(data))
