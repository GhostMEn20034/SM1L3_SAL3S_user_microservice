from rest_framework import serializers

from apps.carts.models import CartItem


class CartItemReplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'
