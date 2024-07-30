from typing import Iterable, List

from django.db.models import QuerySet, When, Case, F

from apps.products.models import Product
from replication_schemas.order_processing.base import ProductItem


class ProductService:
    def __init__(self, product_queryset: QuerySet[Product]):
        self.product_queryset = product_queryset

    @staticmethod
    def _create_when_statements(product_items: Iterable[ProductItem], operation: str) -> List[When]:
        """
        Creates a list of `When` conditions for the bulk update
        """
        if operation == 'reserve':
            return [
                When(object_id=order_item["product_id"], then=F('stock') - order_item["quantity"])
                for order_item in product_items
            ]
        elif operation == 'release':
            return [
                When(object_id=order_item["product_id"], then=F('stock') + order_item["quantity"])
                for order_item in product_items
            ]
        else:
            raise ValueError("Invalid operation. Must be 'reserve' or 'release'.")

    def _bulk_update_stock(self, product_items: Iterable[ProductItem], when_statements: List[When]) -> None:
        """
        Performs the bulk update for the product stock
        """
        self.product_queryset.filter(
            object_id__in=[order_item["product_id"] for order_item in product_items]
        ).update(
            stock=Case(*when_statements)
        )

    def reserve_for_order(self, product_items: Iterable[ProductItem]) -> None:
        """
        Reserves ordered products
        """
        when_statements = self._create_when_statements(product_items, 'reserve')
        self._bulk_update_stock(product_items, when_statements)

    def release_from_order(self, product_items: Iterable[ProductItem]) -> None:
        """
        Returns ordered products from the reservation for the order
        """
        when_statements = self._create_when_statements(product_items, 'release')
        self._bulk_update_stock(product_items, when_statements)
