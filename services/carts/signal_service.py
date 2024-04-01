from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce

from apps.carts.models import Cart, CartItem

class CartSignalService:
    @staticmethod
    def create_cart_on_signup(user_instance):
        Cart.objects.create(user=user_instance)
