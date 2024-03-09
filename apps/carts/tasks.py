from django.utils import timezone
from datetime import timedelta
import logging
import dramatiq
from dramatiq_crontab import cron
from .models import Cart
from django.conf import settings

@cron(f"0 0 */{settings.DELETE_INACTIVE_CARTS_PERIOD_DAYS} * *") # Run Task Every N Hours
@dramatiq.actor
def delete_inactive_carts():
    # Get the time 1 day (24 hours) ago from now
    one_day_ago = timezone.now() - timedelta(days=1)
    logging.info("Deleting inactive carts...")
    Cart.objects.filter(updated_at__lte=one_day_ago, user__isnull=True).delete()
