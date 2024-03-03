from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.state import token_backend
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

class TokenRefreshSerializerForStaff(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        decoded_payload = token_backend.decode(data['access'], verify=True)
        user_id = decoded_payload['user_id']
        user = get_user_model().objects.get(id=user_id)
        if not (user.is_staff or user.is_superuser):
            raise PermissionDenied('You are not authorized to refresh this token.')

        return data
