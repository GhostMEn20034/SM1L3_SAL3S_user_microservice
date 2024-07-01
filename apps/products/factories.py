from decimal import Decimal
from bson import ObjectId
from factory.django import DjangoModelFactory
import factory
from faker import Faker

from .models import Product


fake = Faker()


class ProductFactory(DjangoModelFactory):
    object_id = factory.LazyAttribute(lambda object_id: str(ObjectId()))
    parent_id = factory.LazyAttribute(lambda object_id: str(ObjectId()))
    name = factory.Faker('word')
    price = factory.LazyAttribute(lambda x: Decimal(fake.random_number(digits=5)) / 100)
    discount_rate = factory.LazyAttribute(lambda x: Decimal(fake.random_number(digits=2)) / 100)
    tax_rate = factory.LazyAttribute(lambda x: Decimal(fake.random_number(digits=2)) / 100)
    stock = factory.LazyAttribute(lambda x: fake.random_int(min=1, max=1000))
    max_order_qty = factory.LazyAttribute(lambda x: fake.random_int(min=1, max=40))
    sku = factory.LazyAttribute(
        lambda x: fake.bothify(text='???-########', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    )
    for_sale = factory.LazyFunction(lambda: True)
    image = factory.LazyAttribute(lambda img_url: fake.image_url())
    event_id = factory.LazyAttribute(lambda object_id: str(ObjectId()))

    class Meta:
        model = Product