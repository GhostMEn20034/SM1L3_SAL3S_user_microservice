from rest_framework import serializers
from apps.carts.models import Cart


class CartReplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'