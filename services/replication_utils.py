from typing import Dict, Any, List

from apps.carts.models import Cart, CartItem
from apps.carts.replication_serializers.cart import CartReplicationSerializer
from apps.carts.replication_serializers.cart_item import CartItemReplicationSerializer


def serialize_cart_data(cart: Cart)  -> Dict[str, Any]:
    cart_serializer = CartReplicationSerializer(instance=cart)
    cart_data = cart_serializer.data
    cart_data.pop("id")
    return cart_data

def serialize_many_cart_items(cart_items: List[CartItem]) -> List[Dict[str, Any]]:
    cart_item_serializer = CartItemReplicationSerializer(instance=cart_items, many=True)
    cart_items_data = []
    for cart_item in cart_item_serializer.data:
        cart_item["cart"] = str(cart_item["cart"])
        cart_item["original_id"] = cart_item.pop("id")
        cart_items_data.append(cart_item)

    return cart_items_data
