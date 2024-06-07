from typing import Optional, List

from django.contrib.auth import get_user_model

from apps.carts.models import Cart, CartItem

User = get_user_model()

class ReplicateAccountCreationParams:
    """
    Parameters for replicating of creating a new user account, including user, cart, and optional cart items.
    """
    def __init__(self,  user: User, cart: Cart, cart_items: Optional[List[CartItem]] = None):
        self.user = user
        self.cart = cart
        self.cart_items = cart_items
