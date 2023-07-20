from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenBlacklistView,
    TokenRefreshView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/social/', include('djoser.social.urls')),
    path('api/', include('accounts.urls')),
    path('api/verify/', include('verification.urls')),
    path('api/auth/', include([
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/',TokenRefreshView.as_view() ,name='token_refresh'),
        path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    ])),

]
