from typing import Any
from .replication.create import ProductCreator
from .replication.update import ProductModifier
from .replication.delete import ProductRemover

def handle_message(routing_key: str, message: Any):
    if routing_key == 'products.crud.create.one':
        return ProductCreator().create_one(message)
    elif routing_key == 'products.crud.create.many':
        return ProductCreator().create_many_products(message)
    elif routing_key == 'products.crud.update.one':
        return ProductModifier().update_one_product(message)
    elif routing_key == 'products.crud.update.many':
        return ProductModifier().update_many_products(message)
    elif routing_key == 'products.crud.delete.one':
        return ProductRemover().delete_one_product(message)
    elif routing_key == 'products.crud.delete.many':
        return ProductRemover().delete_many_products(message)
    elif routing_key == 'products.set.discounts':
        return ProductModifier().set_discounts(message)
