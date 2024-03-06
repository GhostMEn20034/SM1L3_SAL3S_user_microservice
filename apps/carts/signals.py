from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from .models import Product
from services.carts.signal_service import CartSignalService


User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        CartSignalService.create_cart_on_signup(user_instance=instance)


@receiver(post_save, sender=Product)
def recalculate_carts_total(sender, instance, created, **kwargs):
    if not created:
        CartSignalService.recalculate_carts_total_on_product_update(product_instance=instance)
