from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from services.carts.cart_service import CartService
from dependencies.service_dependencies.carts import get_cart_service

class CartViewSet(ViewSet):
    """
    ViewSet for retrieving, updating a cart
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cart_service: CartService = get_cart_service()

    def list(self, request, cart_uuid):
        """
        Returns cart item list
        """
        product_ids = request.query_params.get('product_ids')
        if product_ids is not None:
            product_ids = product_ids.split(',')

        if not cart_uuid and not request.user.is_authenticated:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="No cart uuid provided")

        return self.cart_service.get_cart_item_list(cart_uuid, request.user.id, product_ids)

    def retrieve(self, request, cart_uuid):
        """
        Returns cart's details and cart items
        """
        return self.cart_service.get_cart_details(cart_uuid, request.user.id)

    @action(detail=True)
    def get_carts_short_info(self, request, cart_uuid):
        """
        Returns cart's short information and cart items' short information
        """
        cart_filters = self.cart_service.get_cart_filters(cart_uuid, request.user.id)
        return self.cart_service.get_cart_short_info(cart_filters, return_response_object=True)

    @action(detail=True)
    def create_cart_item(self, request, cart_uuid):
        """
        Method to create a cart item
        """
        cart_item_data = request.data
        return self.cart_service.create_cart_item(cart_uuid, cart_item_data)

    @action(detail=True)
    def update_cart_item(self, request, cart_uuid, item_id):
        """
        Method to update a cart item
        """
        new_cart_item_data = request.data
        return self.cart_service.update_cart_item(cart_uuid, item_id, new_cart_item_data)

    @action(detail=True)
    def delete_cart_item(self, request, item_id, cart_uuid):
        """
        Method to delete a cart item
        """
        return self.cart_service.delete_cart_item(cart_uuid, item_id)

    @action(detail=True)
    def clear_cart(self, request, cart_uuid):
        """
        Method to delete all cart's cart items
        """
        return self.cart_service.clear_cart(cart_uuid)
