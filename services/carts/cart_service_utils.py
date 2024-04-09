import uuid
from typing import Union, Tuple, Optional
from django.db.models import QuerySet

from apps.carts.models import CartItem


class CartsServiceUtils:
    def __init__(self, cart_item_queryset: QuerySet[CartItem]):
        self.cart_item_queryset = cart_item_queryset

    def get_cart_item_if_exists(self, cart_uuid: uuid.UUID,
                                item_id: Union[int, str],
                                ) -> Tuple[Optional[CartItem], bool]:
        """
        Gets a cart item if it exists, otherwise returns Nothing.
        :param cart_uuid: uuid of the Cart object.
        :param item_id: PK of the cart item or product id which related to the cart item.
        :return: A tuple containing the cart item and the boolean indicating whether the cart item exists.
        """
        try:
            cart_item_filters = {"cart_id": cart_uuid}
            cart_item_filters.update({"pk": item_id} if isinstance(item_id, int) else {"product_id": item_id})
            cart_item: CartItem = self.cart_item_queryset.get(**cart_item_filters)
            return cart_item, True
        except CartItem.DoesNotExist:
            return None, False
