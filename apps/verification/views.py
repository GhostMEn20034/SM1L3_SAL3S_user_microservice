from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSet

from services.verification.verificaton_service import VerificationService
from dependencies.service_dependencies.verification import get_verification_service


Account = get_user_model()


class VerificationViewSet(ViewSet):
    queryset = Account.objects.all()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.verification_service: VerificationService = get_verification_service(self.queryset)

    @action(detail=True, methods=['post'], url_path='change-email/confirm', url_name='confirm_email_change')
    def verify_change_email(self, request):
        """
           Verifies OTP entered by the user
           Request data:
               - code -- OTP entered by the user
               - new_email -- Email to which the code was sent
           """
        code = request.data.get("code")
        email = request.data.get("new_email")

        error_response = self.verification_service.verify_email_change(email, code)
        if error_response:
            return error_response

        self.verification_service.change_email_on_succeeded_confirmation(request.user.id, new_email=email)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='signup-confirmation', url_name='signup_confirmation')
    def signup_confirmation(self, request):
        """
           Verifies OTP entered by the user to confirm signup
           Request data:
               - code -- The OTP entered by the user
               - token -- A token that contains the payload to identify which user is entered the OTP
        """
        token = request.data.get("token")
        if not token:
            return Response(data={"error": "Confirmation token required"}, status=status.HTTP_400_BAD_REQUEST)

        return self.verification_service.signup_confirmation(token, request.data.get("code"))

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
        token = request.data.get("token")
        if not token:
            return Response(data={"error": "Confirmation token required"}, status=status.HTTP_400_BAD_REQUEST)

        action_type = request.data.get("action_type")
        return self.verification_service.resend_otp(token, action_type)

    @action(detail=True, methods=['post'], url_path='reset-password/confirm',
            url_name='confirm_reset_password_request')
    def confirm_reset_password_request(self, request):
        """
           Verifies OTP entered by the user to confirm password reset
           Request data:
               - code -- The OTP entered by the user
               - token -- A token that contains the payload to identify which user is entered the OTP
        """
        token = request.data.get("token")
        if not token:
            return Response(data={"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

        return self.verification_service.confirm_reset_password_request(token, request.data.get("code"))

    @action(detail=True, methods=['post'], url_path='reset-password/update', url_name='set_new_password')
    def reset_password(self, request):
        """
           Verifies token provided by the user and change user's password
           Request data:
               - password -- New user's password
               - token -- A token that contains the payload to identify which user is entered the password
        """
        token = request.data.get("token")
        if not token:
            return Response(data={"error": "Something went wrong, try to request password reset again"},
                            status=status.HTTP_400_BAD_REQUEST)

        new_password = request.data.get("password")
        return self.verification_service.reset_password(token, new_password)
