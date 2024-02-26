from django.conf import settings
from twilio.rest import Client


def send_code(service_sid, email):
    """
    :param service_sid: sid of the service created in the twilio
    :param email: The email address to which the code will be sent

    Function sends verification code to specified email
    """
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    verification = client.verify.v2.services(service_sid).verifications.create(
        to=email, channel='email'
    )
    assert verification.status == 'pending'