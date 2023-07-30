from django.contrib.auth import get_user_model
from django.contrib.auth.backends import AllowAllUsersModelBackend
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from .exceptions import UnauthorizedException
from .serializers import UserSerializer, UserCreateSerializer, PasswordSerializer, EmailSerializer
from verification import tasks
from .services import encode_email_confirmation_token, decode_email_confirmation_token

Account = get_user_model()


class UserViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Account.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        # Get the default permissions for the viewset
        permission_classes = super().get_permissions()

        # If the action is create, use AllowAny permission
        if self.action == 'create':
            permission_classes = (permissions.AllowAny(),)

        if self.action == 'list':
            permission_classes = (permissions.IsAdminUser(),)

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

            Returns:
            If:
                - email is valid and not already taken
                - password1 and password2 match and contain at least 8 characters
                creates a new user and returns HTTP status code 201 and user data, if not - returns HTTP status code 400
        """
        # Validate the input data using the serializer
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Save data
            user = serializer.save()

            # Send OTP to email specified by user to confirm registration
            tasks.send_code_signup_confirmation.delay(user.email)

            # Form token what will be used for email confirmation
            token = encode_email_confirmation_token(
                {"email": user.email, "id": user.id})

            # Return a success response with the user data
            return Response({"token": token}, status=status.HTTP_201_CREATED)

        else:
            # if serializer is not valid return error message
            error_message = serializer.errors.get(list(serializer.errors)[0])[0]

            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request):
        user = self.get_object()
        serializer = self.serializer_class(user)
        return Response(serializer.data)

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
        serializer = PasswordSerializer(data=request.data)

        if serializer.is_valid():
            # get the validated data
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            # check if the old password is correct
            if not authenticate(email=user.email, password=old_password):
                return Response({'error': 'The old password is incorrect'}, status=status.HTTP_401_UNAUTHORIZED)

            # set the new password
            user.set_password(new_password)
            user.save()
            return Response({'success': 'Password changed successfully'}, status=status.HTTP_200_OK)
        else:
            error_message = serializer.errors.get(list(serializer.errors)[0])[0]

            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

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

        # use the serializer to validate and update the data
        # specify the fields that you want to update
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # use the join and capitalize methods to modify the field names
            field_names = ', '.join([field.replace('_', ' ').capitalize() for field in request.data])
            return Response({'success': f'{field_names} updated successfully'}, status=status.HTTP_200_OK)
        else:

            error_message = serializer.errors.get(list(serializer.errors)[0])[0]

            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='change-email', url_name='change_email')
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
        old_email = user.email
        new_email = request.data.get("new_email")

        # Validate new email
        serializer = EmailSerializer(data={"email": new_email})
        if not serializer.is_valid():
            error_message = serializer.errors.get(list(serializer.errors)[0])[0]
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

        # Check whether new email doesn't match the previous one
        if old_email == new_email:
            return Response(
                {"error": "You've entered the same email. Enter a different email address than your current one"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if there is a user with the new_email
        user_exists = self.queryset.filter(email=new_email).exists()
        if user_exists:
            return Response(
                {"error": "User with the same email already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # if all ok, send OTP to new email address to verify it
        tasks.send_code_to_change_email.delay(request.data.get("new_email"))
        return Response(status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        backend = AllowAllUsersModelBackend()

        user = backend.authenticate(request, email=request.data.get("email"), password=request.data.get("password"))

        if not user:
            raise UnauthorizedException

        if not user.is_active:
            tasks.send_code_signup_confirmation.delay(user.email)
            token = encode_email_confirmation_token({"email": user.email, "id": user.id})
            return Response({"token": token}, status=status.HTTP_400_BAD_REQUEST)

        return super().post(request, *args, **kwargs)

@api_view(['POST'])
def reset_password(request):
    """
        Action for password reset

        Request data:
            - email -- The email to which the OTP will be sent

        Sends OTP to email and returns status HTTP 200 OK if all OK
    """
    email = request.data.get("email")

    # Validate email
    serializer = EmailSerializer(data={"email": email})
    if not serializer.is_valid():
        error_message = serializer.errors.get(list(serializer.errors)[0])[0]
        return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

    # Check if there is not a user with this email
    user = Account.objects.filter(email=email).first()
    if not user:
        return Response(
            {"error": "User with this email doesn't exist"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create token that will be used for OTP resend
    token = encode_email_confirmation_token({"email": user.email, "id": user.id})

    # Send the OTP to email specified by the user
    tasks.send_code_reset_password.delay(user.email)
    return Response(data={"token": token},status=status.HTTP_200_OK)
