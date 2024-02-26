from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/social/', include('djoser.social.urls')),
    path('api/', include('apps.accounts.urls')),
    path('api/', include('apps.verification.urls')),
    path('api/', include('apps.addresses.urls'))
]
