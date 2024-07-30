from apps.carts.models import Cart, CartItem
from apps.products.models import Product
from services.carts.cart_service import CartService
from services.carts.cart_service_utils import CartsServiceUtils


def get_cart_service() -> CartService:
    cart_item_queryset = CartItem.objects.all()
    cart_queryset = Cart.objects.all()
    product_queryset = Product.objects.all()
    cart_service_utils = CartsServiceUtils(cart_item_queryset)

    return CartService(cart_queryset, cart_item_queryset, product_queryset,
                       cart_service_utils)
