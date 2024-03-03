from rest_framework import permissions


class CartPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['retrieve', 'delete_cart_item', 'update_cart_item', 'clear_cart']:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if view.action in ['update', 'partial_update', 'retrieve']:
            if request.user.is_authenticated:
                return obj.user == request.user or request.user.is_admin

            return obj.user is None or request.user.is_admin
        else:
            return False
