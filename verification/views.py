from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSet
from twilio.base.exceptions import TwilioRestException
from .services import check_code_to_change_email, check_code_signup_confirmation
from accounts.services import change_email, decode_email_confirmation_token, get_tokens_for_user, \
    encode_email_confirmation_token
from . import tasks

Account = get_user_model()


class VerificationViewSet(ViewSet):
    queryset = Account.objects.all()

    @action(detail=True, methods=['post'], url_path='change-email', url_name='verify_change_email')
    def verify_change_email(self, request):
        """
           Verifies OTP entered by the user
           Request data:
               - code -- OTP entered by the user
               - new_email -- Email to which the code was sent
           """
        code = request.data.get("code")
        email = request.data.get("new_email")

        try:
            verified = check_code_to_change_email(email, code)
        except TwilioRestException:
            return Response({"error": "a code message has not been sent to this email"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not verified:
            return Response({"error": "The code is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        changed_user = change_email(user_id=request.user.id, new_email=email)
        if changed_user:
            return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='signup-confirmation', url_name='signup_confirmation')
    def signup_confirmation(self, request):
        token = request.data.get("token")
        code = request.data.get("code")

        token_payload_data = decode_email_confirmation_token(token)

        user = self.queryset.filter(email=token_payload_data.get("email"),
                                    id=token_payload_data.get("id")).first()

        if not user:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "User doesn't exists"})

        try:
            verified = check_code_signup_confirmation(token_payload_data.get("email"), code)
        except TwilioRestException:
            return Response({"error": "a code message has not been sent to this email"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not verified:
            return Response({"error": "The code is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save(update_fields=['is_active'])

        return Response(status=status.HTTP_200_OK, data=get_tokens_for_user(user))

    @action(detail=True, methods=['post'], url_path='resend-otp', url_name='resend_otp')
    def resend_otp(self, request):
        """
            Action for OTP resend
            Request data:
                - token -- token that stores user email and id
                - action_type -- type of the email that will be sent to user
                (for example signup-confirmation or reset-password-confirmation)
            Returns:
                if:
                    - token is valid
                    - there is user with email decoded from token
                    returns HTTP code 200 and resends OTP
                if
                    - token is not valid or there's no user with email decoded from token
                    returns HTTP code 400 and error message
        """
        action_type = request.data.get("action_type")
        token_payload = decode_email_confirmation_token(request.data.get("token"))
        user = self.queryset.filter(email=token_payload.get("email"),
                                    id=token_payload.get("id")).first()

        if not user:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "User doesn't exists"})

        if action_type == 'signup-confirmation':
            tasks.send_code_signup_confirmation.delay(user.email)

        new_token = encode_email_confirmation_token({"email": token_payload["email"], "id": token_payload["id"]})
        return Response(status=status.HTTP_200_OK, data={"token": new_token})
