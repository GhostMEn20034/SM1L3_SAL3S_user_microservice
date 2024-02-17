from django.conf import settings
from twilio.rest import Client

class CodeChecker:
    def __init__(self):
        self.__client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    def _check_code(self, service_sid, email, code):
        """
        :param service_sid: sid of the service created in the twilio
        :param email: The email address to which the code was sent
        :param code: Code entered by the user on the client side

        Function verifies the code that was sent to the user's email.
        Returns True if the user entered a correct verification code.
        """
        verification = self.__client.verify.v2.services(service_sid).verification_checks.create(
            to=email, code=code
        )
        return verification.status == 'approved'

    def check_code_to_change_email(self, email, code):
        return self._check_code(settings.TWILIO_SERVICE_SID_CHANGE_EMAIL, email, code)

    def check_code_signup_confirmation(self, email, code):
        return self._check_code(settings.TWILIO_SERVICE_SID_SIGNUP_CONFIRMATION, email, code)

    def check_code_password_reset(self, email, code):
        return self._check_code(settings.TWILIO_SERVICE_SID_PASSWORD_RESET, email, code)
