from rest_framework import serializers

from .models import Cart, CartItem
from apps.products.models import Product



class ProductCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('object_id', 'name', 'stock', 'max_order_qty', 'price', 'discount_rate', 'image')

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductCartItemSerializer(read_only=True)


    class Meta:
        model = CartItem
        exclude = ('cart', )


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        exclude = ('user', 'created_at', 'updated_at')
