import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum, F, ExpressionWrapper
from django.db.models.functions import Coalesce

from apps.products.models import Product


User = get_user_model()


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart", null=True, blank=True)
    cart_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def count(self):
        """
        Returns the total number of items in the cart
        """
        return self.items.aggregate(
            total_quantity=Sum('quantity')
        )['total_quantity'] or 0

    @property
    def total(self):
        """
        Returns the total cost of all items in the cart, accounting for any discounts on products.
        The total is dynamically calculated from the cart items, using the product's price and discount rate.
        """
        result = self.items.annotate(
                discounted_price=ExpressionWrapper(F('quantity') * (
                        F('product__price') - (F('product__price') * Coalesce(F('product__discount_rate'), 0))
                ), output_field=models.DecimalField())
            ).aggregate(
                total=Sum('discounted_price'),
            )['total'] or 0.00
        return round(result, 2)

    def clear(self):
        """
        Removes all items from the cart.
        """
        self.items.all().delete()

    def __str__(self):
        return f"Cart of {self.user.email}" if self.user else str(self.cart_uuid)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, to_field='object_id')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
