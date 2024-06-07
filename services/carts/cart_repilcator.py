import uuid
from typing import List, Dict, Any

from apps.carts.replication_serializers.cart_item import CartItemReplicationSerializer
from apps.carts.models import Cart, CartItem
from apps.core.tasks import perform_data_replication
from ..replication_utils import serialize_cart_data, serialize_many_cart_items


class CartReplicator:
    """
    Replicates user's carts and cart items between all "subscribed" microservices.
    """
    def __init__(self):
        self.base_routing_key_name_carts = 'users.carts'
        self.base_routing_key_name_cart_items = 'users.cart_items'

    @staticmethod
    def __serialize_cart(cart: Cart) -> Dict[str, Any]:
        return serialize_cart_data(cart)

    @staticmethod
    def __serialize_one_cart_item(cart_item: CartItem) -> Dict[str, Any]:
        cart_item_serializer = CartItemReplicationSerializer(instance=cart_item)
        cart_item_data = cart_item_serializer.data
        cart_item_data["cart"] = str(cart_item_data["cart"])
        cart_item_data["original_id"] = cart_item_data.pop("id")
        return cart_item_data

    @staticmethod
    def __serialize_many_cart_items(cart_items: List[CartItem]) -> List[Dict[str, Any]]:
        return serialize_many_cart_items(cart_items)

    def replicate_cart_creation(self, cart: Cart):
        routing_key = self.base_routing_key_name_carts + '.create.one'
        cart_data = self.__serialize_cart(cart)
        perform_data_replication.send(routing_key, cart_data)

    def replicate_cart_clearance(self, cart_uuid: uuid.UUID):
        routing_key = self.base_routing_key_name_carts + '.clear'
        perform_data_replication.send(routing_key, {"cart_uuid": cart_uuid})

    def replicate_one_cart_item_creation(self, cart_item: CartItem):
        routing_key = self.base_routing_key_name_cart_items + '.create.one'
        cart_item_data = self.__serialize_one_cart_item(cart_item)
        perform_data_replication.send(routing_key, cart_item_data)

    def replicate_one_cart_item_update(self, cart_item: CartItem):
        routing_key = self.base_routing_key_name_cart_items + '.update.one'
        cart_item_data = self.__serialize_one_cart_item(cart_item)
        perform_data_replication.send(routing_key, cart_item_data)

    def replicate_many_cart_items_creation(self, cart_items: List[CartItem]):
        routing_key = self.base_routing_key_name_cart_items + '.create.many'
        cart_items_data = self.__serialize_many_cart_items(cart_items)
        perform_data_replication.send(routing_key, cart_items_data)

    def replicate_one_cart_item_removal(self, cart_item_id: int):
        routing_key = self.base_routing_key_name_cart_items + '.delete.one'
        perform_data_replication.send(routing_key, {"cart_item_id": cart_item_id})

