from django.db import transaction
from django.db.models import F
from rest_framework import serializers

from ..models import RecentlyViewedItem
from apps.products.models import Product


class _ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('name', 'price', 'discount_rate', 'image', 'object_id', 'for_sale', 'stock')


class RecentlyViewedItemSerializer(serializers.ModelSerializer):
    item = _ProductSerializer(source='product', read_only=True)

    class Meta:
        model = RecentlyViewedItem
        read_only_fields = ('last_seen', 'created_at', )
        fields = ('id', 'product', 'item', 'user', 'created_at', 'last_seen', 'view_count')
        extra_kwargs = {'product': {'write_only': True}}

    def create(self, validated_data) -> RecentlyViewedItem:
        product = validated_data.get('product')
        user = validated_data.get('user')
        with transaction.atomic():
            recently_viewed_item, _ = RecentlyViewedItem.objects.update_or_create(
                user=user,
                product_id=product.object_id,
                defaults={'view_count': F('view_count') + 1},
                create_defaults={"user": user, "product_id": product.object_id}
            )
            recently_viewed_item.refresh_from_db()

        return recently_viewed_item
