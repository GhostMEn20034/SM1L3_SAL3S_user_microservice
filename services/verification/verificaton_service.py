from typing import Union, Optional
from rest_framework import status
from rest_framework.response import Response
from twilio.base.exceptions import TwilioRestException

from apps.accounts.serializers.serializers import EmailSerializer
from services.accounts.common import get_tokens_for_user
from services.confirmation_token_codec import ConfirmationTokenCodec
from apps.verification import tasks
from services.verification.code_checker import CodeChecker

class VerificationService:
    def __init__(self, account_queryset):
        self.account_queryset = account_queryset

    def reset_password_request(self, email) -> Union[Response, bytes]:
        # Validate email
        serializer = EmailSerializer(data={"email": email})
        if not serializer.is_valid():
            error_message = serializer.errors.get(list(serializer.errors)[0])[0]
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

        # Check if there is not a user with this email
        user = self.account_queryset.filter(email=email).first()
        if not user:
            return Response(
                {"error": "User with this email doesn't exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Create token that will be used for OTP resend
        token = ConfirmationTokenCodec.encode_email_confirmation_token({"email": user.email, "id": user.id})
        # Send the OTP to email specified by the user
        tasks.send_code_reset_password.send(user.email)
        return token

    def verify_email_change(self, email, code) -> Optional[Response]:
        """
        :param code: OTP entered by the user
        :param email: Email to which the code was sent
        """
        try:
            code_checker = CodeChecker()
            verified = code_checker.check_code_to_change_email(email, code)
        except TwilioRestException:
            return Response({"error": "a code message has not been sent to this email"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not verified:
            return Response({"error": "The code is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

    def _verify_code(self, token, code, check_function):
        """
            A helper function that verifies the code entered by the user.
            :param token: Confirmation token.
            :param code: OTP Code.
            :param check_function: The function that checks the code validity

            Returns:
                - user: The user instance if verification succeeds, None otherwise
                - response: The error response if verification fails, None otherwise
            """
        token_payload = ConfirmationTokenCodec.decode_email_confirmation_token(token)

        # Get the user from the queryset based on the email and id from the payload data
        user = self.account_queryset.filter(email=token_payload.get("email"),
                               id=token_payload.get("id")).first()

        # Check if the user exists and return an error response if not
        if not user:
            response = Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "User doesn't exists"})
            return None, response

        # Try to verify the code using the check function and return an error response if it fails
        try:
            verified = check_function(token_payload.get("email"), code)
        except TwilioRestException:
            response = Response({"error": "a code message has not been sent to this email"},
                                status=status.HTTP_400_BAD_REQUEST)
            return None, response

        if not verified:
            response = Response({"error": "The code is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
            return None, response

        # Return the user instance and None as response if verification succeeds
        return user, None

    def signup_confirmation(self, token, code):
        code_checker = CodeChecker()
        user, response = self._verify_code(token, code, code_checker.check_code_signup_confirmation)
        # If response is not None, it means verification failed, and we return the error response
        if response:
            return response

        user.is_active = True
        user.save(update_fields=['is_active'])
        return Response(status=status.HTTP_200_OK, data=get_tokens_for_user(user))

    def resend_otp(self, token, action_type):
        token_payload = ConfirmationTokenCodec.decode_email_confirmation_token(token)
        user = self.account_queryset.filter(email=token_payload.get("email"),
                                    id=token_payload.get("id")).first()

        if not user:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "User doesn't exists"})

        if action_type == 'signup-confirmation':
            tasks.send_code_signup_confirmation.send(user.email)
        elif action_type == 'reset-password':
            tasks.send_code_reset_password.send(user.email)

        new_token = ConfirmationTokenCodec.encode_email_confirmation_token(
            {"email": token_payload["email"], "id": token_payload["id"]})
        return Response(status=status.HTTP_200_OK, data={"token": new_token})


    def confirm_reset_password_request(self, token, code):
        code_checker = CodeChecker()
        # Call the verify_code function with the request, queryset, and check_code_password_reset function
        user, response = self._verify_code(token, code, code_checker.check_code_password_reset)
        # If response is not None, it means verification failed, and we return the error response
        if response:
            return response

        new_token = ConfirmationTokenCodec.encode_email_confirmation_token(
            {"email": user.email, "id": user.id}, 5)
        return Response(data={"token": new_token}, status=status.HTTP_200_OK)

    def reset_password(self, token, new_password):
        """
        Check user's confirmation token and reset password
        """
        token_payload = ConfirmationTokenCodec.decode_email_confirmation_token(token)

        # Get the user from the queryset based on the email and id from the payload data
        user = self.account_queryset.filter(email=token_payload.get("email"),
                                    id=token_payload.get("id")).first()
        # Check if the user exists and return an error response if not
        if not user:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "User doesn't exists"})

        if len(new_password) < 8:
            # Return an error response with a message and status code 400
            return Response({"error": "The new password must have at least 8 characters"},
                            status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response(data=get_tokens_for_user(user), status=status.HTTP_200_OK)
