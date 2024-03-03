from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from .permissions import CartPermission
from services.carts.cart_service import CartService
from dependencies.service_dependencies.carts import get_cart_service

class CartViewSet(ViewSet):
    """
    ViewSet for retrieving, updating a cart
    """
    permission_classes = (CartPermission, )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cart_service: CartService = get_cart_service()

    def retrieve(self, request, cart_uuid):
        return self.cart_service.get_cart(cart_uuid)

    @action(detail=True)
    def create_cart_item(self, request, cart_uuid):
        cart_item_data = request.data
        return self.cart_service.create_cart_item(cart_uuid, cart_item_data)

    @action(detail=True)
    def update_cart_item(self, request, cart_uuid, item_id):
        new_cart_item_data = request.data
        return self.cart_service.update_cart_item(cart_uuid, item_id, new_cart_item_data)

    @action(detail=True)
    def delete_cart_item(self, request, item_id, cart_uuid):
        return self.cart_service.delete_cart_item(cart_uuid, item_id)

    @action(detail=True)
    def clear_cart(self, request, cart_uuid):
        return self.cart_service.clear_cart(cart_uuid)
