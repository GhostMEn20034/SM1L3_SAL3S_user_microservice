from typing import Optional
from logging import error
from apps.products.serializers.update import ProductSerializer
from apps.products.models import Product
from django.db import transaction


class ProductModifier:
    def update_one_product(self, data: dict) -> Optional[dict]:
        try:
            product = Product.objects.get(object_id=data.pop("object_id", None))
        except Product.DoesNotExist:
            error("Cannot find product to update")
            return None

        data = ProductSerializer(instance=product, data=data, partial=True)
        if data.is_valid():
            data.save()
            return data.data
        else:
            error(data.errors)

    def update_many_products(self, data: list[dict]):
        grouped_data = {item["object_id"]: item for item in data}
        queryset = Product.objects.filter(object_id__in=[object_id for object_id in grouped_data.keys()])
        with transaction.atomic():
            for product in queryset:
                serializer = ProductSerializer(instance=product, data=grouped_data[product.object_id], partial=True)
                serializer.is_valid(raise_exception=False)
                serializer.save()

    def set_discounts(self, data: dict):
        product_ids = data.get("product_ids", [])
        discounts = data.get("discounts")

        queryset = Product.objects.filter(object_id__in=product_ids)
        if discounts is None:
            queryset.update(discount_rate=None)
        else:
            discount_mapping = {_id: discount for _id, discount in zip(product_ids, discounts)}
            with transaction.atomic():
                for product in queryset:
                    product.discount_rate = discount_mapping[product.object_id]
                    product.save()
