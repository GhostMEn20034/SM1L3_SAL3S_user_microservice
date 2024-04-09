from apps.carts.models import Cart
from rest_framework import serializers


class CartSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField(read_only=True)
    count = serializers.SerializerMethodField(read_only=True)

    def get_total(self, obj):
        return obj.total

    def get_count(self, obj):
        return obj.count

    class Meta:
        model = Cart
        exclude = ('user', 'created_at', 'updated_at')
