from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Product(models.Model):
    # Original product's identifier from the product microservice
    object_id = models.CharField(db_index=True, unique=True)
    # parent product's identifier from the product microservice
    parent_id = models.CharField(db_index=True, null=True, blank=True)
    name = models.CharField()
    price = models.DecimalField(max_digits=13 ,decimal_places=2, db_index=True)
    # Coefficient where 0.00 means 0% discount and 1 means 100% discount
    discount_rate = models.DecimalField(decimal_places=2, max_digits=3, blank=True, null=True, validators=[
        MinValueValidator(0),
        MaxValueValidator(1)
    ], db_index=True)
    # Coefficient where 0.00 means 0% tax and 1 means 100% tax
    tax_rate = models.DecimalField(decimal_places=2, max_digits=3, validators=[
        MinValueValidator(0),
        MaxValueValidator(1)
    ], db_index=True)
    stock = models.PositiveIntegerField(default=0, )
    # Maximum count of product available on one order
    max_order_qty = models.PositiveIntegerField(default=0, )
    sku = models.CharField()
    # Can product be sold?
    for_sale = models.BooleanField(default=True, db_index=True)
    image = models.URLField()

    def is_able_to_add_to_cart(self, new_quantity) -> bool:
        if not self.for_sale:
            return False

        return new_quantity <= self.stock and new_quantity <= self.max_order_qty

    def __str__(self):
        return self.name