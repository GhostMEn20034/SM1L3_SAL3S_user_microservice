from djoser.social.token.jwt import TokenStrategy
from rest_framework_simplejwt.tokens import RefreshToken

class CustomTokenStrategy(TokenStrategy):

    @classmethod
    def obtain(cls, user):
        refresh = RefreshToken.for_user(user)
        refresh["first_name"] = user.first_name
        refresh["last_name"] = user.last_name
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            # "user": user,
        }