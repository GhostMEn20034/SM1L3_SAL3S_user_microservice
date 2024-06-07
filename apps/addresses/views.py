from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from services.addresses.address_replicator import AddressReplicator
from .serializers import AddressModelSerializer
from .models import Address
from .permssions import IsAdminOrOwner

class AddressModelViewSet(ModelViewSet):
    serializer_class = AddressModelSerializer
    permission_classes = (IsAdminOrOwner, )
    queryset = Address.objects.all()

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.address_replicator = AddressReplicator()

    def get_queryset(self):
        # Get the current user from the request
        user = self.request.user

        # Filter addresses by the user field
        queryset = Address.objects.filter(user=user)
        return queryset

    def perform_write_operation(self, serializer):
        instance = serializer.save()
        return instance

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = self.perform_write_operation(serializer)
        self.address_replicator.replicate_address_creation(address)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        address = self.perform_write_operation(serializer)
        self.address_replicator.replicate_address_update(address)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        address = self.get_object()
        address.user = None
        address.save()
        self.address_replicator.replicate_address_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
