from datetime import datetime
from decimal import Decimal
from typing import Union, Optional

from apps.carts.models import CartItem


class CartSynchronizer:
    """
    A class that syncs the cart's data with the cart items.
    It provides methods to manually sync a cart
    """

    def __init__(self, cart_item: CartItem):
        self.cart_item = cart_item

    def _save_cart(self, subtotal: Union[int, float, Decimal],
                   quantity: Optional[int] = None, action: str = 'add'):
        """
        Saves the cart to db with new data
        :param subtotal: how much the cart total price should be increased / decreased.
        :param quantity: how much the cart total count should be increased / decreased.
        :param action: Which action to perf
        """
        quantity = quantity if quantity is not None else self.cart_item.quantity

        if action == 'subtract':
            self.cart_item.cart.total -= subtotal
            self.cart_item.cart.count -= quantity
        elif action == 'add':
            self.cart_item.cart.total += subtotal
            self.cart_item.cart.count += quantity

        self.cart_item.cart.updated_at = datetime.now()
        self.cart_item.cart.save()

    def _cart_item_delete(self):
        """
        Deletes the cart item from the db.
        Also resets the cart's total price if the cart's count is 0.
        """
        item_before_delete = CartItem.objects.get(id=self.cart_item.id)
        discount_rate = item_before_delete.product.discount_rate \
            if item_before_delete.product.discount_rate is not None else 0

        subtotal = item_before_delete.quantity * (
                item_before_delete.product.price - (item_before_delete.product.price * discount_rate))

        item_before_delete.cart.count -= item_before_delete.quantity
        if item_before_delete.cart.count == 0:
            item_before_delete.cart.total = 0
        else:
            item_before_delete.cart.total -= subtotal

        item_before_delete.cart.updated_at = datetime.now()
        item_before_delete.cart.save()

    def sync_cart_item_create(self):
        """
        Creates a new cart item and increase cart's total price on subtotal value.
        Also increases the cart's total count of items.
        """
        discount_rate = self.cart_item.product.discount_rate if self.cart_item.product.discount_rate is not None else 0
        subtotal = self.cart_item.quantity * (
                self.cart_item.product.price - (self.cart_item.product.price * discount_rate))

        self._save_cart(subtotal)

    def sync_cart_item_update(self):
        """
        Updates the cart item.
        - if new quantity is 0, the cart item will be deleted.
        - if the difference of old quantity and new quantity is greater than 0,
        the cart's total price will be increased on the product's price with discount multiplied by difference
        and cart's total count will be increased on difference.
        - if the difference of old quantity and new quantity is less than 0,
        the cart's total price will be decreased on the product's price with discount multiplied by abs of difference
        and cart's total count will be decreased on abs of difference.
        - if the difference of old quantity and new quantity is 0, nothing will happen.
        """
        item_before_update = CartItem.objects.get(id=self.cart_item.id)

        discount_rate = item_before_update.product.discount_rate \
            if item_before_update.product.discount_rate is not None else 0

        difference = self.cart_item.quantity - item_before_update.quantity
        if difference > 0:
            subtotal_to_add = difference * (
                    item_before_update.product.price - (item_before_update.product.price * discount_rate))
            self._save_cart(subtotal_to_add, difference, 'add')
            return None

        if difference < 0:
            subtotal_to_subtract = abs(difference) * (
                    item_before_update.product.price - (item_before_update.product.price * discount_rate))
            self._save_cart(subtotal_to_subtract, abs(difference), 'subtract')

    def sync_cart_item_delete(self):
        self._cart_item_delete()
