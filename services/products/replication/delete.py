from logging import error
from django.db.models import Q

from apps.products.models import Product

class ProductRemover:

    def delete_one_product(self ,message_body: dict):
        object_id = message_body.get('_id', '')
        try:
            product = Product.objects.get(object_id=object_id)
            product.delete()
        except Product.DoesNotExist:
            error("Cannot find product to delete")


    def delete_many_products(self, filters: dict):
        object_ids = filters.get("product_ids", [])
        parent_ids = filters.get("parent_ids", [])
        Product.objects.filter(
            Q(object_id__in=object_ids) | Q(parent_id__in=parent_ids)
        ).delete()
