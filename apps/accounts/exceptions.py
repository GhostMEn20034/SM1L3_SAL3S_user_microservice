from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_401_UNAUTHORIZED

class UnauthorizedException(APIException):
    status_code = HTTP_401_UNAUTHORIZED
    default_detail = "No active account found with the given credentials"
    default_code = "unauthorized"


class TokenExpiredException(APIException):
    status_code = HTTP_401_UNAUTHORIZED
    default_detail = "Session expired, send code again"
    default_code = "token_expired"