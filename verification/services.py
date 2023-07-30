from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from accounts.services import decode_email_confirmation_token
from rest_framework.response import Response
from rest_framework import status


client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def send_code(service_sid, email):
    """
    :param service_sid - sid of the service created in the twilio
    :param email - The email address to which the code will be sent

    Function sends verification code to specified email
    """
    verification = client.verify.v2.services(service_sid).verifications.create(
        to=email, channel='email'
    )
    assert verification.status == 'pending'

def check_code(service_sid, email, code):
    """
    :param service_sid - sid of the service created in the twilio
    :param email - The email address to which the code was sent
    :param code - Code entered by the user on the client side

    Function verifies the code that was sent to the user's email.
    Returns True if the user entered a correct verification code.
    """
    verification = client.verify.v2.services(service_sid).verification_checks.create(
        to=email, code=code
    )
    return verification.status == 'approved'

def check_code_to_change_email(email, code):
    return check_code(settings.TWILIO_SERVICE_SID_CHANGE_EMAIL, email, code)

def check_code_signup_confirmation(email, code):
    return check_code(settings.TWILIO_SERVICE_SID_SIGNUP_CONFIRMATION, email, code)

def check_code_password_reset(email, code):
    return check_code(settings.TWILIO_SERVICE_SID_PASSWORD_RESET, email, code)

def verify_code(request, queryset, check_function):
    """
        A helper function that verifies the code entered by the user.

        Parameters:
            - request: The request object
            - queryset: The queryset of users
            - check_function: The function that checks the code validity
            - exp: The expiration time of the token (optional)

        Returns:
            - user: The user instance if verification succeeds, None otherwise
            - response: The error response if verification fails, None otherwise
        """
    token = request.data.get("token")
    code = request.data.get("code")
    token_payload = decode_email_confirmation_token(token)

    # Get the user from the queryset based on the email and id from the payload data
    user = queryset.filter(email=token_payload.get("email"),
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
