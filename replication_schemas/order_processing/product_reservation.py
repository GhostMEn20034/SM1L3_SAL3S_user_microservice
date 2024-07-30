from typing import TypedDict, List

from .base import ProductItem


class ProductReservationData(TypedDict):
    user_id: int
    products: List[ProductItem]
