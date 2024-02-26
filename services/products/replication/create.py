import logging
from apps.products.serializers.create import ProductSerializer
from apps.products.models import Product


class ProductCreator:
    def create_one(self, data: dict) -> dict:
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return serializer.validated_data
        else:
            logging.error(serializer.errors)
            logging.info("Unable to serialize data and create product")

    def _validate_products(self, data: list[dict]) -> list[dict]:
        serializer = ProductSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def create_many_products(self, data: list[dict]) -> list[Product]:
        validated_data = self._validate_products(data)
        data_set = list()
        for data in validated_data:
            data_set.append(Product(**data))

        products = Product.objects.bulk_create(data_set)
        return products
