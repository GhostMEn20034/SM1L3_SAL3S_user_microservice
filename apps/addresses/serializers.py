from rest_framework import serializers
from django_countries.serializer_fields import CountryField
from .models import Address
from phonenumber_field.serializerfields import PhoneNumberField

class AddressModelSerializer(serializers.ModelSerializer):
    country = CountryField(country_dict=True)
    phone_number = PhoneNumberField()
    class Meta:
        model = Address
        exclude = ('user', )

    def create(self, validated_data):
        # Get the user from the request context
        user = self.context["request"].user
        # Create a new address instance with the validated data
        address = Address.objects.create(user=user, **validated_data)
        return address


class AddressReplicationSerializer(serializers.ModelSerializer):
    country = CountryField()
    phone_number = PhoneNumberField()
    class Meta:
        model = Address
        fields = '__all__'
