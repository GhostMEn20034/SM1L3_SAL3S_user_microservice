from django.urls import path, include
from . import views
from .routers import UserRouter

router = UserRouter()
router.register('user', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls))
]
