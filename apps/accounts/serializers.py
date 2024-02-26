from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField

User = get_user_model()


class UserSerializerAllFields(serializers.ModelSerializer):
    """Serializer for getting all user's information"""
    class Meta:
        model = User
        exclude = ('password', )


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for getting part of user's information
    """
    email = serializers.EmailField(max_length=256, read_only=True)
    first_name = serializers.CharField(max_length=50, error_messages={'blank': "First Name cannot be blank"})
    last_name = serializers.CharField(max_length=50, allow_blank=True)
    date_of_birth = serializers.DateField(allow_null=True)
    sex = serializers.ChoiceField(choices=User.SEX_CHOICES, allow_blank=True, write_only=True)
    phone_number = PhoneNumberField()
    sex_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'date_of_birth', 'sex',
                  'phone_number', 'sex_display')

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


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=256, error_messages={"blank": "Email field must not be blank"})


class OAuthUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password')


class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, write_only=True,
                                   error_messages={"blank": "Email field must not be blank"})
    first_name = serializers.CharField(max_length=30, write_only=True,
                                       error_messages={"blank": "First name field must not be blank"})
    last_name = serializers.CharField(max_length=30, write_only=True, allow_blank=True)
    password1 = serializers.CharField(write_only=True, min_length=8,
                                      error_messages={"blank": "Enter password in both fields",
                                                      "min_length": "Password must have at least 8 characters"})
    password2 = serializers.CharField(write_only=True, min_length=8,
                                      error_messages={"blank": "Enter password in both fields",
                                                      "min_length": "Password must have at least 8 characters"})

    # Define a custom validation method for the email field
    def validate_email(self, value):
        # Check if there is any user with the same email
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already taken')
        return value

    # Define a custom validation method for the passwords
    def validate(self, data):
        # Check if the passwords match
        if data['password1'] != data['password2']:
            raise serializers.ValidationError('Passwords do not match')
        return data

    def save(self, **kwargs):
        # Get the validated data
        email = self.validated_data['email']
        password = self.validated_data['password1']
        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        # Create a new user instance
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=False
        )
        # Return the user instance
        return user
