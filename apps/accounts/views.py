from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from services.accounts.account_service import AccountService
from .serializers import UserSerializer
from services.verification.verificaton_service import VerificationService
from .permissions import IsMicroservice

Account = get_user_model()


class UserViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Account.objects.all()
    serializer_class = UserSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_service = AccountService(account_queryset=self.queryset,
                                              user_serializer=self.serializer_class)

    def get_permissions(self):
        # Get the default permissions for the viewset
        permission_classes = super().get_permissions()
        # If the action is create, use AllowAny permission
        if self.action == 'create':
            permission_classes = (permissions.AllowAny(),)

        return permission_classes

    def get_object(self):
        user_id = self.request.user.id
        obj = self.queryset.get(id=user_id)
        return obj

    def create(self, request):
        """
        Action for user creation.
        Request data:
            email: user's email address
            password1: user's password
            password2: confirmation of user's password
            first_name: user's first name
            last_name: user's last name

            If:
                - email is valid and not already taken
                - password1 and password2 match and contain at least 8 characters
                creates a new user and returns HTTP status code 201 and user data, if not - returns HTTP status code 400
        """
        return self.account_service.create_user(request.data)

    def retrieve(self, request):
        user = self.get_object()
        return self.account_service.get_user(user)

    @action(detail=True, methods=['patch'], url_path='change-password', url_name='change_password')
    def change_password(self, request):
        """
        Action for password change.

        Request data:
            old_password: user's current password
            new_password: The password the user wants to set
            new_password_confirmation: Confirmation of new_password

        Returns:
            If:
                - new_password contains at least 8 characters
                - new_password and new_password_confirmation matches
                - old_password is correct
            returns HTTP status code 200 and changes password, if not - returns HTTP status code 400
        """
        user = self.get_object()
        return self.account_service.change_password(user, request.data)

    @action(detail=True, methods=['patch'], url_path='update-info', url_name='update_info')
    def update_info(self, request):
        """
        Action to update user fields

        Request data:
            - field to update
        Returns:
            if:
                - serializer data is not valid
                returns HTTP code 400
            if:
                - serializer data is valid
                updates fields in the user model
                and returns HTTP code 200
        """
        user = self.get_object()
        return self.account_service.update_user(user, request.data)

    @action(detail=True, methods=['post'], url_path='change-email/request', url_name='change_email_request')
    def change_email(self, request):
        """
        Action for email change

        Request data:
            - new_email -- email what will be new user email
        Returns:
            if:
                - serializer is valid
                send code on new email
                and returns HTTP code 200
            if
                - serializer is not valid
                returns HTTP code 400 and error message
        """
        user = self.get_object()
        new_email = request.data.get("new_email")
        return self.account_service.change_email(user, new_email)

    @action(detail=True, methods=['get'], url_path='full-info', permission_classes=[permissions.AllowAny, ])
    def get_full_information(self, request):
        """
        Action that returns user's information, cart data.
        If user is not authenticated, it returns only cart data.
        If there's no cart data, it returns new cart for anonymous user.
        """
        user_id = request.user.id
        return self.account_service.get_full_user_info(user_id)

    @action(detail=True, methods=['post'], url_path='check',
            url_name='check_user', permission_classes=[IsMicroservice, ])
    def check_user(self, request):
        """
        THis route checks whether the user exists and if it does,
        it will return all user's data.
        Request Body:
        user_id int
        microservice_key str - since this route is only for microservices communication,
                               it requires a special key to ensure that
                               this request is made by another microservice.
        """
        user_id = request.data.get("user_id")
        return self.account_service.check_user(user_id)


@api_view(['POST'])
def reset_password(request):
    """
        Action for password reset

        Request data:
            - email -- The email to which the OTP will be sent

        Sends OTP to email and returns status HTTP 200 OK if all OK
    """
    email = request.data.get("email")
    verification_service = VerificationService(Account.objects.all())
    token = verification_service.reset_password_request(email)
    return Response(data={"token": token}, status=status.HTTP_200_OK)
