from django.urls import path, include
from . import views
from.custom_obtain_tokens_view import CustomTokenObtainPairView
from .routers import UserRouter
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenRefreshView
)

router = UserRouter()
router.register('user', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include([
        path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    ])),
    path('user/reset-password/request', views.reset_password, name='reset_password_request')
]
