from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

Account = get_user_model()

def change_email(user_id, new_email):
    user = Account.objects.get(id=user_id)
    user.email = new_email
    user.save(update_fields=['email'])
    return True

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
