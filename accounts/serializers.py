from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=256, read_only=True)
    first_name = serializers.CharField(max_length=50, error_messages={'blank': "First Name cannot be blank"})
    last_name = serializers.CharField(max_length=50, allow_blank=True)
    date_of_birth = serializers.DateField(allow_null=True)
    sex = serializers.ChoiceField(choices=User.SEX_CHOICES, allow_blank=True, write_only=True)
    phone_number = PhoneNumberField()
    sex_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'date_of_birth', 'sex', 'phone_number', 'sex_display')

    def get_sex_display(self, obj):
        return obj.get_sex_display()


class PasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True,
                                         error_messages={'blank': 'Old password may not be blank'})
    new_password = serializers.CharField(max_length=128, write_only=True,
                                         error_messages={'blank': 'Enter the new password in both fields'})
    new_password_confirmation = serializers.CharField(max_length=128, write_only=True,
                                                      error_messages={'blank': 'Enter the new password in both fields'})

    def validate(self, data):

        # check whether match the new password and the password confirmation
        if data['new_password'] != data['new_password_confirmation']:
            raise serializers.ValidationError("New passwords do not match")

        # check if the new password contains at least 8 characters long
        if len(data['new_password']) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")

        # if everything is fine, return data
        return data


class ChangeEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField(max_length=256, error_messages={"blank": "Email field must not be blank"})


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password')

