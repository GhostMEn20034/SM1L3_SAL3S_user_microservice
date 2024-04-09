from rest_framework import serializers

from apps.carts.models import CartItem


class CreateCartItemSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    product_id = serializers.CharField(min_length=1)
    quantity = serializers.IntegerField(default=1)
