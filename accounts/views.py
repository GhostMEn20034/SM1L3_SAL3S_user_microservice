from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .serializers import UserSerializer, PasswordSerializer, ChangeEmailSerializer
from verification.tasks import send_code_to_change_email

Account = get_user_model()

class UserViewSet(viewsets.ViewSet):

    permission_classes = (permissions.IsAuthenticated, )
    queryset = Account.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        user_id = self.request.user.id
        obj = self.queryset.get(id=user_id)
        return obj

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
                returns HTTP code 200
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
                returns HTTP code 200
            if
                - serializer is not valid
                returns HTTP code 400 and error message
        """
        user = self.get_object()
        old_email = user.email
        new_email = request.data.get("new_email")
        if old_email == new_email:
            return Response(
                {"error": "You've entered the same email. Enter a different email address than your current one"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ChangeEmailSerializer(data=request.data)
        if serializer.is_valid():
            send_code_to_change_email.delay(request.data.get("new_email"))
            return Response(status=status.HTTP_200_OK)
        else:
            error_message = serializer.errors.get(list(serializer.errors)[0])[0]
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)
