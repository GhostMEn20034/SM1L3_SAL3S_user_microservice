from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from twilio.base.exceptions import TwilioRestException
from .services import check_code_to_change_email
from accounts.services import change_email


@api_view(['POST'])
def verify_change_email(request):
    """
    Verifies OTP entered by the user
    Request data:
        - code -- OTP entered by the user
        - new_email -- Email to which the code was sent
    """
    code = request.data.get("code")
    email = request.data.get("new_email")

    try:
        verified = check_code_to_change_email(email, code)
    except TwilioRestException:
        return Response({"error": "a code message has not been sent to this email"},
                        status=status.HTTP_400_BAD_REQUEST)

    if not verified:
        return Response({"error": "The code is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

    changed_user = change_email(user_id=request.user.id, new_email=email)
    if changed_user:
        return Response(status=status.HTTP_200_OK)
