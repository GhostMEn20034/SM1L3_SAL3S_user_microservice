from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        path('', include('apps.accounts.urls')),
        path('', include('apps.verification.urls')),
        path('', include('apps.addresses.urls')),
        path('', include('apps.carts.urls')),
        path('', include('apps.history.urls')),
    ])),
]
