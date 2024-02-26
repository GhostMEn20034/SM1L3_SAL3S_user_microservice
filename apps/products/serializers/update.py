from rest_framework.serializers import ModelSerializer
from ..models import Product


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'object_id': {'read_only': True},
            'parent_id': {'read_only': True},
        }
