from apps.carts.models import Cart, CartItem
from services.carts.cart_service import CartService

def get_cart_service() -> CartService:
    return CartService(Cart.objects.all(), CartItem.objects.all())
