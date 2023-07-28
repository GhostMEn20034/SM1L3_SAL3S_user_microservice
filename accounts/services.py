import base64
import json
import datetime
from .exceptions import SignupTokenExpiredException
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

Account = get_user_model()

def change_email(user_id, new_email):
    user = Account.objects.get(id=user_id)
    user.email = new_email
    user.save(update_fields=['email'])
    return True


def encode_email_confirmation_token(data_to_encode):
    """
    Encodes dictionary to base64 bytes
    """
    now = datetime.datetime.now()
    data_to_encode["exp"] = str(now + datetime.timedelta(minutes=10))
    json_string = json.dumps(data_to_encode)
    base64_bytes = base64.b64encode(json_string.encode())
    return base64_bytes


def decode_email_confirmation_token(token):
    """
    Decodes token with user information encoded by base64
    """
    json_strings = base64.b64decode(token).decode()
    dict_object = json.loads(json_strings)
    now_dt = datetime.datetime.now()
    exp = dict_object.get("exp")
    exp_dt = datetime.datetime.strptime(exp, "%Y-%m-%d %H:%M:%S.%f")
    if exp_dt < now_dt:
        raise SignupTokenExpiredException

    return dict_object

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
