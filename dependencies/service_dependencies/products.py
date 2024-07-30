from apps.products.models import Product
from services.products.product_service import ProductService


def get_product_service() -> ProductService:
    product_queryset = Product.objects.all()
    return ProductService(product_queryset, )
