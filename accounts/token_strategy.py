from djoser.social.token.jwt import TokenStrategy
from rest_framework_simplejwt.tokens import RefreshToken

class CustomTokenStrategy(TokenStrategy):

    @classmethod
    def obtain(cls, user):
        refresh = RefreshToken.for_user(user)
        full_name = user.first_name if not user.last_name else f"{user.first_name} {user.last_name}"
        refresh["full_name"] = full_name
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            # "user": user,
        }