from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import logging
import dramatiq
from dramatiq_crontab import cron

from .models import Cart
from apps.core.tasks import perform_data_topic_replication


@cron(f"0 0 */{settings.DELETE_INACTIVE_CARTS_PERIOD_DAYS} * *") # Run Task Every N Days
@dramatiq.actor
def delete_inactive_carts():
    # Get the time 1 day (24 hours) ago from now
    one_day_ago = timezone.now() - timedelta(days=1)
    logging.info("Deleting inactive carts...")
    Cart.objects.filter(updated_at__lte=one_day_ago, user__isnull=True).delete()
    perform_data_topic_replication.send(
        settings.USERS_DATA_CRUD_EXCHANGE_TOPIC_NAME,
        'users.carts.delete_inactive_carts', {"updated_at_lte": str(one_day_ago), },
    )
