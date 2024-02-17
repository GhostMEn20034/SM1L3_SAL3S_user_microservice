import base64
import json
from datetime import datetime, timedelta
from apps.accounts.exceptions import TokenExpiredException


class ConfirmationTokenCodec:
    """
    Responsible for encoding / decoding confirmation token
    """
    @staticmethod
    def encode_email_confirmation_token(data_to_encode, exp=10):
        """
        Encodes dictionary to base64 bytes
        :param data_to_encode -- data that will be encoded
        :param exp - time expiration of token (In minutes)
        """
        now = datetime.now()
        data_to_encode["exp"] = str(now + timedelta(minutes=exp))
        json_string = json.dumps(data_to_encode)
        base64_bytes = base64.b64encode(json_string.encode())
        return base64_bytes

    @staticmethod
    def decode_email_confirmation_token(token):
        """
        Decodes token with user information encoded by base64
        """
        json_strings = base64.b64decode(token).decode()
        dict_object = json.loads(json_strings)
        now_dt = datetime.now()
        exp = dict_object.get("exp")
        exp_dt = datetime.strptime(exp, "%Y-%m-%d %H:%M:%S.%f")
        if exp_dt < now_dt:
            raise TokenExpiredException

        return dict_object
