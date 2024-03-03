from django.urls import path, include

from .url_patterns import get_url_patterns

urlpatterns = [
    path('carts/', include(get_url_patterns()), )
]