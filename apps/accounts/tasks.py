import logging
import dramatiq
from dramatiq_crontab import cron
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.utils import aware_utcnow
from django.conf import settings


@cron(f"0 */{settings.FLUSH_EXPIRED_TOKEN_INTERVAL_HOURS} * * *") # Run Task Every N Hours
@dramatiq.actor
def flush_expired_tokens():
    logging.info("Flushing expired tokens...")
    OutstandingToken.objects.filter(expires_at__lte=aware_utcnow()).delete()
