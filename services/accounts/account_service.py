from rest_framework import status
from rest_framework.response import Response

from apps.accounts.serializers import UserCreateSerializer, PasswordSerializer, EmailSerializer
from services.confirmation_token_codec import ConfirmationTokenCodec
# from apps.verification import tasks
from django.contrib.auth import authenticate


class AccountService:
    def __init__(self, account_queryset, user_serializer):
        self.account_queryset = account_queryset
        self.user_serializer = user_serializer

    def create_user(self, data):
        serializer = UserCreateSerializer(data=data)
        if serializer.is_valid():
            # Save data
            user = serializer.save()
            # Send OTP to email specified by user to confirm registration
            # tasks.send_code_signup_confirmation.delay(user.email)
            # Form token what will be used for email confirmation
            token = ConfirmationTokenCodec.encode_email_confirmation_token(
                {"email": user.email, "id": user.id})
            # Return a success response with the user data
            return Response({"token": token}, status=status.HTTP_201_CREATED)
        else:
            # if serializer is not valid return error message
            error_message = serializer.errors.get(list(serializer.errors)[0])[0]
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

    def get_user(self, user_data):
        serializer = self.user_serializer(user_data)
        return Response(serializer.data)

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
        # tasks.send_code_to_change_email.delay(new_email)
        return Response(status=status.HTTP_200_OK)
