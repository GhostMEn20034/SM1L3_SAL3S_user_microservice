from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model

from apps.products.models import Product

User = get_user_model()


class RecentlyViewedItem(models.Model):
    """
    Represents a recently viewed item in the user's history.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                to_field="object_id", related_name="recently_viewed_items")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    view_count = models.IntegerField(default=1, validators=[MinValueValidator(1),])
    last_seen = models.DateTimeField(auto_now=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} Viewed By {self.user.email}"
