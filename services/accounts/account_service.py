from rest_framework import status
from rest_framework.response import Response

from services.carts.cart_service import CartService
from apps.accounts.serializers.serializers import (
    UserCreateSerializer,
    PasswordSerializer,
    EmailSerializer,
    UserSerializerAllFields
)
from services.confirmation_token_codec import ConfirmationTokenCodec
from apps.verification import tasks
from django.contrib.auth import authenticate, get_user_model

Account = get_user_model()

class AccountService:
    def __init__(self, account_queryset, user_serializer, cart_service):
        self.account_queryset = account_queryset
        self.user_serializer = user_serializer
        self.cart_service: CartService = cart_service

    def get_user(self, user_data):
        serializer = self.user_serializer(user_data)
        return Response(serializer.data)

    def find_user_by_id(self, user_id):
        try:
            user = self.account_queryset.get(pk=user_id)
            return user, None
        except Account.DoesNotExist:
            return None, Response(status=status.HTTP_404_NOT_FOUND, data={"error": "User not found"})

    def create_user(self, data):
        # get cart uuid from which we need to copy cart items
        copy_cart_items_from = data.get('copy_cart_items_from')

        serializer = UserCreateSerializer(data=data)
        if serializer.is_valid():
            # Save data
            user = serializer.save()
            print(user.email)
            # Send OTP to email specified by user to confirm registration
            tasks.send_code_signup_confirmation.send(user.email)
            # Form token what will be used for email confirmation
            token = ConfirmationTokenCodec.encode_email_confirmation_token(
                {"email": user.email, "id": user.id})

            if copy_cart_items_from is not None:
                self.cart_service.copy_cart_items(user.id, copy_cart_items_from)

            # Return a success response with the user data
            return Response({"token": token}, status=status.HTTP_201_CREATED)
        else:
            # if serializer is not valid return error message
            error_message = serializer.errors.get(list(serializer.errors)[0])[0]
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)



    def change_password(self, user_object, request_data):
        serializer = PasswordSerializer(data=request_data)
        if serializer.is_valid():
            # get the validated data
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            # check if the old password is correct
            if not authenticate(email=user_object.email, password=old_password):
                return Response({'error': 'The old password is incorrect'}, status=status.HTTP_401_UNAUTHORIZED)
            # set the new password
            user_object.set_password(new_password)
            user_object.save()
            return Response({'success': 'Password changed successfully'}, status=status.HTTP_200_OK)
        else:
            error_message = serializer.errors.get(list(serializer.errors)[0])[0]
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

    def update_user(self, user_object, request_data):
        # use the serializer to validate and update the data
        # specify the fields that you want to update
        serializer = self.user_serializer(user_object, data=request_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # use the join and capitalize methods to modify the field names
            field_names = ', '.join([field.replace('_', ' ').capitalize() for field in request_data])
            return Response({'success': f'{field_names} updated successfully'}, status=status.HTTP_200_OK)

        error_message = serializer.errors.get(list(serializer.errors)[0])[0]
        return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

    def change_email(self, user_object, new_email):
        old_email = user_object.email

        # Validate new email
        serializer = EmailSerializer(data={"email": new_email})
        if not serializer.is_valid():
            error_message = serializer.errors.get(list(serializer.errors)[0])[0]
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

        # Check whether new email doesn't match the previous one
        if old_email == new_email:
            return Response(
                {"error": "You've entered the same email. Enter a different email address than your current one"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if there is a user with the new_email
        user_exists = self.account_queryset.filter(email=new_email).exists()
        if user_exists:
            return Response(
                {"error": "User with the same email already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # if all ok, send OTP to new email address to verify it
        tasks.send_code_to_change_email.send(new_email)
        return Response(status=status.HTTP_200_OK)


    def get_full_user_info(self, user_id, cart_uuid=None):
        """
        Returns user information and his cart.
        if user is anonymous then, it returns only cart and empty user field.
        :param user_id: User's identifier.
        :param cart_uuid: Cart's uuid identifier.
        """
        user, _ = self.find_user_by_id(user_id)
        if user is not None:
            serializer = self.user_serializer(instance=user)
            user = serializer.data
        else:
            user = None

        cart = self.cart_service.get_by_uuid_or_create_cart(cart_uuid, user_id)
        response_data = {"user": user, "cart": cart}

        if user is None:
            response_data["cart_uuid"] = cart.get("cart_uuid")

        return Response(data=response_data, status=status.HTTP_200_OK)

    def check_user(self, user_id):
        user, error_response = self.find_user_by_id(user_id)
        if error_response:
            return error_response

        serializer = UserSerializerAllFields(instance=user)
        return Response(serializer.data)
