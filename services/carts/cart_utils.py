from uuid import uuid4
from .cart_service import CartService
from dependencies.service_dependencies.carts import get_cart_service


def clone_cart_items(cart_owner_id: int, cart_uuid: uuid4):
    """
    Clones the cart items from the one cart to another
    :param cart_owner_id: owner id of the cart to which we want to clone cart items
    :param cart_uuid: uuid of the cart from which we want to clone cart items
    """
    cart_service: CartService = get_cart_service()
    cart_service.copy_cart_items(cart_owner_id, cart_uuid)
