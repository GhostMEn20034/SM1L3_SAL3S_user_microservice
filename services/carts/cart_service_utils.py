import uuid
from typing import Union, Tuple, Optional, List, Dict, Any
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

    @staticmethod
    def get_filters_for_cart_item_list(user_id: int, cart_item_ids: List[Union[int, str]]) -> Dict[str, Any]:
        filters = {}
        if all(isinstance(id_, int) for id_ in cart_item_ids):
            # All IDs are integers
            filters["id__in"] =  cart_item_ids
        elif all(isinstance(id_, str) for id_ in cart_item_ids):
            # All IDs are strings
            filters["product_id__in"] = cart_item_ids
        else:
            raise ValueError("All items in cart_item_ids must be of the same type (either all int or all str).")

        filters["cart__user_id"] = user_id
        return filters
