from django.conf import settings
from twilio.rest import Client


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
