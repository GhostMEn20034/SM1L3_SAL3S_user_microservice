from django.db import transaction

from dependencies.service_dependencies.carts import get_cart_service
from dependencies.service_dependencies.products import get_product_service
from replication_schemas.order_processing.product_release import ProductReleaseData
from replication_schemas.order_processing.product_reservation import ProductReservationData


class OrderProcessingHandler:
    @staticmethod
    def reserve_products_and_remove_cart_items(data: ProductReservationData) -> None:
        cart_service = get_cart_service()
        product_service = get_product_service()
        with transaction.atomic():
            # Get all product_ids, that will be used for cart_items removal
            product_ids = [product["product_id"] for product in data["products"]]
            # Delete cart items that were used for order creation
            cart_service.delete_many_cart_items(data["user_id"], product_ids)
            # Reserve products for order
            product_service.reserve_for_order(data["products"])

    @staticmethod
    def release_products(data: ProductReleaseData) -> None:
        product_service = get_product_service()
        with transaction.atomic():
            # Return back products from order reservation
            product_service.release_from_order(data["products"])
