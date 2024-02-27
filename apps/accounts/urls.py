from django.urls import path, include
from . import views
from .custom_obtain_tokens_views import (
    TokenObtainPairViewForRegularUsers,
    TokenObtainPairViewForStaff,
    TokenRefreshViewForStaff
)
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
        path('token/', TokenObtainPairViewForRegularUsers.as_view(), name='token_obtain_pair'),
        path('staff-token/', TokenObtainPairViewForStaff.as_view(), name='staff_token_obtain_pair'),
        path('staff-token/refresh/', TokenRefreshViewForStaff.as_view(), name='staff_token_refresh'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    ])),
    path('user/reset-password/request', views.reset_password, name='reset_password_request')
]
