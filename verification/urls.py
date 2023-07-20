from django.urls import path
from .views import verify_change_email

urlpatterns = [
    path('user/change-email/', verify_change_email, name='verify_change_email')
]
