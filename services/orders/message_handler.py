from typing import Any
from services.orders.replication.order_processing import OrderProcessingHandler


def handle_message(routing_key: str, message: Any) -> None:
    base_routing_key = "orders"

    if routing_key == base_routing_key + ".products.reserve_and_remove_cart_items":
        return OrderProcessingHandler.reserve_products_and_remove_cart_items(message)
    elif routing_key == base_routing_key + ".products.release":
        return OrderProcessingHandler.release_products(message)
