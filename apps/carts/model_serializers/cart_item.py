from rest_framework import serializers

from apps.carts.models import CartItem
from apps.products.models import Product


class ProductCartItemSerializer(serializers.ModelSerializer):
    discounted_price = serializers.ReadOnlyField()
    tax_amount = serializers.ReadOnlyField()
    tax_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ('object_id', 'name', 'stock', 'max_order_qty', 'discounted_price', 'tax_amount',
                  'tax_percentage', 'price', 'discount_rate', 'image', 'for_sale', 'tax_rate')


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        exclude = ('cart',)


class CartItemWithProductSerializer(CartItemSerializer):
    total_item_price = serializers.ReadOnlyField()
    total_item_tax = serializers.ReadOnlyField()
    product = ProductCartItemSerializer(read_only=True)

