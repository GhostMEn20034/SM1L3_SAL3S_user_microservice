from djoser.social.token.jwt import TokenStrategy
from rest_framework_simplejwt.tokens import RefreshToken

class CustomTokenStrategy(TokenStrategy):

    @classmethod
    def obtain(cls, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }