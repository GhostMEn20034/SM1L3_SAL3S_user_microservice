from django.urls import path, include
from .routers import VerificationRouter
from .views import VerificationViewSet

router = VerificationRouter()
router.register('verification', VerificationViewSet, basename='verification')

urlpatterns = [
    path('', include(router.urls))
]
