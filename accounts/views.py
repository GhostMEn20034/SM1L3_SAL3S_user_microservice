from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .serializers import UserSerializer, PasswordSerializer

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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='update-info', url_name='update_info')
    def update_info(self, request):
        """
        Action to update user fields

        Request data:
            field: field to update
            value: value of field
        Returns:
            if:
                - field parameter is "email"
                returns HTTP code 400
            if:
                - serializer data is valid
                updates field in the user model
                returns HTTP code 200
        """
        user = self.get_object()

        # get the field name from the request data
        field = request.data.get('field')

        print(request.data)

        if field == 'email':
            return Response({'error': 'Email field cannot be updated'}, status=status.HTTP_400_BAD_REQUEST)

        # use the serializer to validate and update the data
        serializer = self.serializer_class(user, data={field: request.data.get('value')}, partial=True)
        if serializer.is_valid():
            serializer.save()

            # use the replace and capitalize methods to modify the field name
            field = field.replace('_', ' ').capitalize()

            return Response({'success':  f'{field} updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
