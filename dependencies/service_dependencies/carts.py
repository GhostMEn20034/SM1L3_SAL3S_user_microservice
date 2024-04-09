from apps.carts.models import Cart, CartItem
from apps.products.models import Product
from services.carts.cart_service import CartService
from services.carts.cart_service_utils import CartsServiceUtils


def get_cart_service() -> CartService:
    cart_item_queryset = CartItem.objects.all()
    return CartService(Cart.objects.all(), cart_item_queryset, Product.objects.all(),
                       CartsServiceUtils(cart_item_queryset))
