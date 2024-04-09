from rest_framework import serializers

from apps.carts.models import CartItem
from apps.products.models import Product


class ProductCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('object_id', 'name', 'stock', 'max_order_qty', 'price', 'discount_rate', 'image')


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        exclude = ('cart',)


class CartItemWithProductSerializer(CartItemSerializer):
    product = ProductCartItemSerializer(read_only=True)
