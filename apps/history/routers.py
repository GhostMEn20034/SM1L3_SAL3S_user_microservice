from rest_framework.routers import SimpleRouter

from .views import HistoryViewSet

history_router = SimpleRouter()
history_router.register('history', HistoryViewSet, basename='history')
