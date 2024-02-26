from django.contrib.auth.backends import AllowAllUsersModelBackend
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .exceptions import UnauthorizedException
from services.confirmation_token_codec import ConfirmationTokenCodec
from apps.verification import tasks


class CustomTokenObtainPairView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        backend = AllowAllUsersModelBackend()

        user = backend.authenticate(request, email=request.data.get("email"), password=request.data.get("password"))

        if not user:
            raise UnauthorizedException

        if not user.is_active:
            tasks.send_code_signup_confirmation.send(user.email)
            token = ConfirmationTokenCodec.encode_email_confirmation_token({"email": user.email, "id": user.id})
            return Response({"token": token}, status=status.HTTP_400_BAD_REQUEST)

        return super().post(request, *args, **kwargs)