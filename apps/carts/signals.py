from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from services.carts.signal_service import CartSignalService


User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        CartSignalService.create_cart_on_signup(user_instance=instance)
