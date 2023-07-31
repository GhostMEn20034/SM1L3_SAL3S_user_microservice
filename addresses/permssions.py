from rest_framework.permissions import BasePermission

class IsAdminOrOwner(BasePermission):

    def has_permission(self, request, view):
        # Check if the user is authenticated or is an admin user
        return request.user and (request.user.is_authenticated or request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        # Check if the user is an admin user or the owner of the address
        return request.user and (request.user.is_staff or request.user == obj.user)
