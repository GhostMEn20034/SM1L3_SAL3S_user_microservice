from django.http import QueryDict
from rest_framework import mixins, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import RecentlyViewedItem
from .serializers.model_serializers import RecentlyViewedItemSerializer
from .pagination import RecentlyViewedItemsPagination


class HistoryViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """
    A viewset that provides actions:
     - list all viewed items (products) in the user's history.
     - create a new viewed item in the user's history.
     - remove (destroy) a viewed item from the user's history
     - remove all viewed items from the user's history.
    """
    serializer_class = RecentlyViewedItemSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = RecentlyViewedItemsPagination

    def get_queryset(self):
        return RecentlyViewedItem.objects.filter(user=self.request.user) \
            .select_related('product').order_by('-last_seen')

    def create(self, request, *args, **kwargs):
        serializer_raw_data = {"user": request.user.id, **request.data}
        serializer = self.get_serializer(data=serializer_raw_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # If viewed item has view_count greater than 1, it means it already exists,
        # so HTTP 204 status will be returned.
        if serializer.data.get("view_count", 1) > 1:
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT, headers=headers)
        # If viewed item has view_count equals to 1, it means that viewed item were created just now,
        # so HTTP 201 status will be returned.
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['DELETE', ], url_path='delete-all', url_name='destroy_all')
    def destroy_all(self, request):
        queryset = self.get_queryset()
        deleted_viewed_items_count, _ = queryset.delete()
        return Response(
            {'message': f'Deleted {deleted_viewed_items_count} items.'},
            status=status.HTTP_200_OK
        )
