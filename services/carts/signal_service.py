from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce

from apps.carts.models import Cart, CartItem

class CartSignalService:
    @staticmethod
    def create_cart_on_signup(user_instance):
        Cart.objects.create(user=user_instance)

    @staticmethod
    def recalculate_carts_total_on_product_update(product_instance):
        # Get all cart items with the updated product
        cart_items = CartItem.objects.filter(product=product_instance) \
            .select_related('cart').values_list('cart', flat=True).distinct()
        carts = Cart.objects.filter(pk__in=cart_items)

        for cart in carts:
            # Calculate the total considering the discount, replacing null with 0
            cart.total = cart.items.annotate(
                discounted_price=ExpressionWrapper(F('quantity') * (
                        F('product__price') - (F('product__price') * Coalesce(F('product__discount_rate'), 0))
                ), output_field=DecimalField())
            ).aggregate(
                total=Sum('discounted_price'),
            )['total'] or 0
            cart.save()
