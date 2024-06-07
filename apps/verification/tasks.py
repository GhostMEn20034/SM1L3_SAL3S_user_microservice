import dramatiq
import logging

from django.conf import settings
from services.verification.send_code import send_code


@dramatiq.actor
def send_code_to_change_email(email):
    send_code(settings.TWILIO_SERVICE_SID_CHANGE_EMAIL, email)


@dramatiq.actor
def send_code_signup_confirmation(email):
    logging.info(f"Sending confirmation code to {email}")
    send_code(settings.TWILIO_SERVICE_SID_SIGNUP_CONFIRMATION, email)


@dramatiq.actor
def send_code_reset_password(email):
    logging.info(f"Sending code reset password to {email}")
    send_code(settings.TWILIO_SERVICE_SID_PASSWORD_RESET, email)
