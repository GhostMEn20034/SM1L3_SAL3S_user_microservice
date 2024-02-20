from rest_framework import permissions
from django.conf import settings


class IsMicroservice(permissions.BasePermission):
    """
    Custom permission to only allow requests with a valid MICROSERVICE_KEY in the body.
    """
    def has_permission(self, request, view):
        """
        If there is a valid MICROSERVICE_KEY in the request body,
        then access to the route is allowed.
        """
        if 'microservice_key' not in request.data:
            return False

        if request.data['microservice_key'] != settings.MICROSERVICE_KEY:
            return False

        return True
