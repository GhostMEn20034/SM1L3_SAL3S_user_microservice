from django.conf import settings
from .services import send_code
from celery import shared_task


@shared_task
def send_code_to_change_email(email):
    send_code(settings.TWILIO_SERVICE_SID_CHANGE_EMAIL, email)


@shared_task
def send_code_signup_confirmation(email):
    send_code(settings.TWILIO_SERVICE_SID_SIGNUP_CONFIRMATION, email)
