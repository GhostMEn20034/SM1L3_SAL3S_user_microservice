from rest_framework.viewsets import ModelViewSet
from .serializers import AddressModelSerializer
from .models import Address
from .permssions import IsAdminOrOwner

class AddressModelViewSet(ModelViewSet):
    serializer_class = AddressModelSerializer
    permission_classes = (IsAdminOrOwner, )
    queryset = Address.objects.all()

    def get_queryset(self):
        # Get the current user from the request
        user = self.request.user

        # Filter addresses by the user field
        queryset = Address.objects.filter(user=user)
        return queryset
