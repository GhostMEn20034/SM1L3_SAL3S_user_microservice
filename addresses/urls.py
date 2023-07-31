from django.urls import path, include
from rest_framework import routers
from .views import AddressModelViewSet

router = routers.SimpleRouter()
router.register(r'addresses', AddressModelViewSet)

urlpatterns = [
    path('', include(router.urls))
]
