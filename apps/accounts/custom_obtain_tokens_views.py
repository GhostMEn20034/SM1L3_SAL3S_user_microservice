from django.contrib.auth.backends import AllowAllUsersModelBackend
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .exceptions import UnauthorizedException
from .serializers.token_serializers import TokenRefreshSerializerForStaff
from services.confirmation_token_codec import ConfirmationTokenCodec
from apps.verification import tasks
from services.carts.cart_utils import clone_cart_items


class TokenObtainPairViewForRegularUsers(TokenObtainPairView):
    """
    Custom token obtain/refresh view for regular users.
    """
    def post(self, request, *args, **kwargs):
        backend = AllowAllUsersModelBackend()

        user = backend.authenticate(request, email=request.data.get("email"), password=request.data.get("password"))

        if not user:
            raise UnauthorizedException

        if cart_uuid := request.data.get("copy_cart_items_from"):
            clone_cart_items(user.id, cart_uuid)

        if not user.is_active:
            tasks.send_code_signup_confirmation.send(user.email)
            token = ConfirmationTokenCodec.encode_email_confirmation_token({"email": user.email, "id": user.id})
            return Response({"token": token}, status=status.HTTP_400_BAD_REQUEST)

        return super().post(request, *args, **kwargs)


class TokenObtainPairViewForStaff(TokenObtainPairView):
    """
    Custom token obtain/refresh view for staff users
    """
    def post(self, request, *args, **kwargs):
        backend = AllowAllUsersModelBackend()

        user = backend.authenticate(request, email=request.data.get("email"), password=request.data.get("password"))

        if not user:
            raise UnauthorizedException

        if not user.is_staff or not user.is_superuser:
            raise PermissionDenied

        return super().post(request, *args, **kwargs)


class TokenRefreshViewForStaff(TokenRefreshView):
    serializer_class = TokenRefreshSerializerForStaff
