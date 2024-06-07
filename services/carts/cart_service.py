import uuid
from typing import Optional, Union, List, Dict, Tuple, Any
from django.db import transaction
from django.db.models import QuerySet
from rest_framework.response import Response
from rest_framework import status

from apps.carts.models import Cart, CartItem
from apps.products.models import Product
from apps.carts.model_serializers.cart_item import CartItemWithProductSerializer, CartItemSerializer
from apps.carts.model_serializers.cart import CartSerializer
from apps.carts.serializers.cart_item import CreateCartItemSerializer
from .cart_repilcator import CartReplicator
from .cart_service_utils import CartsServiceUtils


class CartService:
    def __init__(self, cart_queryset, cart_item_queryset, product_queryset, cart_service_utils):
        self.cart_queryset: QuerySet[Cart] = cart_queryset
        self.cart_item_queryset: QuerySet[CartItem] = cart_item_queryset
        self.product_queryset: QuerySet[Product] = product_queryset
        self.cart_service_utils: CartsServiceUtils = cart_service_utils
        self.cart_replicator = CartReplicator()

    def get_cart_filters(self, cart_uuid: uuid.UUID, user_id: Optional[int] = None) -> Dict:
        cart_filters = {}
        if user_id is not None:
            cart_filters['user_id'] = user_id
        else:
            cart_filters['cart_uuid'] = cart_uuid

        return cart_filters

    def get_cart_details(self, cart_uuid: uuid.UUID) -> Tuple[Cart, QuerySet[CartItem]]:
        cart: Cart = self.cart_queryset.get(cart_uuid=cart_uuid)
        cart_items = cart.items.select_related('product') \
            .only('quantity', 'product__max_order_qty', 'product__stock',
                  'product__object_id', 'product__name',
                  'product__price', 'product__discount_rate', 'product__image', )
        return cart, cart_items

    def get_cart_short_info(self, cart_filters: dict, return_response_object: bool = False) \
            -> Union[Dict[str, Any], Response]:
        cart: Cart = self.cart_queryset.prefetch_related('items').get(**cart_filters)
        cart_serializer = CartSerializer(instance=cart)
        cart_validated_data = cart_serializer.data

        cart_items = {
            cart_item.product_id: {"quantity": cart_item.quantity}
            for cart_item in CartItem.objects.filter(cart=cart)
        }
        cart_validated_data["items"] = cart_items
        return cart_validated_data if not return_response_object \
            else Response(cart_validated_data, status.HTTP_200_OK)

    def get_by_uuid_or_create_cart(self, cart_uuid: uuid.UUID, user_id: Optional[int]) -> Dict[str, Any]:
        try:
            cart_filters = self.get_cart_filters(cart_uuid, user_id)
            return self.get_cart_short_info(cart_filters)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(user_id=user_id)
            cart.save()
            self.cart_replicator.replicate_cart_creation(cart)

            serializer = CartSerializer(instance=cart)
            cart_data = serializer.data

            cart_data["items"] = {}
            cart_data["count"] = 0

            return cart_data

    def copy_cart_items(self, user_id: int, cart_uuid: uuid.UUID) -> Optional[List[CartItem]]:
        with transaction.atomic():
            try:
                old_cart: Cart = self.cart_queryset.get(cart_uuid=cart_uuid)
                new_cart: Cart = self.cart_queryset.get(user_id=user_id)
            except Cart.DoesNotExist:
                return None

            cart_items: QuerySet[CartItem] = self.cart_item_queryset.filter(cart=old_cart)
            cloned_cart_items = []
            for cart_item in cart_items:
                cart_item.id = None
                cart_item.cart = new_cart
                cloned_cart_items.append(cart_item)

            inserted_cart_items = self.cart_item_queryset.bulk_create(cloned_cart_items)
            return inserted_cart_items

    def get_cart(self, cart_uuid: uuid.UUID) -> Response:
        cart, cart_items = self.get_cart_details(cart_uuid)
        cart_serializer = CartSerializer(instance=cart)
        cart_item_serializer = CartItemWithProductSerializer(instance=cart_items, many=True)
        return Response(
            data={"cart": cart_serializer.data, "cart_items": cart_item_serializer.data},
            status=status.HTTP_200_OK,
        )

    def create_cart_item(self, cart_uuid: uuid.UUID, data: dict) -> Response:
        create_cart_serializer = CreateCartItemSerializer(data={"cart_id": cart_uuid, **data})
        if not create_cart_serializer.is_valid():
            return Response(create_cart_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = create_cart_serializer.validated_data

        if not self.cart_queryset.filter(cart_uuid=cart_uuid).exists():
            return Response({"error": "Cart with specified cart_id does not exist"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            product: Product = self.product_queryset.get(object_id=validated_data.get("product_id"))
        except Product.DoesNotExist:
            return Response({"error": "Specified product does not exist"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not product.is_able_to_add_to_cart(validated_data.get("quantity")):
            return Response({"error": "Not able to add a product to the cart"},
                            status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.change_quantity_or_create(validated_data)

        cart_item_serializer = CartItemSerializer(cart_item)

        if created:
            self.cart_replicator.replicate_one_cart_item_creation(cart_item)
            return Response(status=status.HTTP_201_CREATED, data={"cart_item": cart_item_serializer.data,
                                                                  "created": True})

        self.cart_replicator.replicate_one_cart_item_update(cart_item)
        return Response(status=status.HTTP_204_NO_CONTENT, data={"cart_item": cart_item_serializer.data,
                                                                 "created": False})

    def update_cart_item(self, cart_uuid: uuid.UUID, item_id: Union[int, str], data: dict) -> Response:
        if isinstance(item_id, str) and item_id.isdigit():
            item_id = int(item_id)

        cart_item, exists = self.cart_service_utils.get_cart_item_if_exists(cart_uuid, item_id)
        if not exists:
            return Response({"error": "Cart or its item does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartItemWithProductSerializer(instance=cart_item, data=data)
        if serializer.is_valid():
            cart_quantity = serializer.validated_data.get("quantity")
            if cart_quantity > 0:
                cart_item.quantity = serializer.validated_data.get("quantity")
                cart_item.save()
                self.cart_replicator.replicate_one_cart_item_update(cart_item)
            else:
                cart_item_id = cart_item.id
                cart_item.delete()
                self.cart_replicator.replicate_one_cart_item_removal(cart_item_id)

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete_cart_item(self, cart_uuid: uuid.UUID, item_id: Union[int, str]) -> Response:
        if isinstance(item_id, str) and item_id.isdigit():
            item_id = int(item_id)

        cart_item, exists = self.cart_service_utils.get_cart_item_if_exists(cart_uuid, item_id)
        if not exists:
            return Response({"error": "Cart or its item does not exist"}, status=status.HTTP_404_NOT_FOUND)

        cart_item_id = cart_item.id
        cart_item.delete()

        self.cart_replicator.replicate_one_cart_item_removal(cart_item_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def clear_cart(self, cart_uuid: uuid.UUID) -> Response:
        try:
            cart: Cart = self.cart_queryset.get(cart_uuid=cart_uuid)
        except Cart.DoesNotExist:
            return Response({"error": "Cart does not exist"}, status=status.HTTP_404_NOT_FOUND)

        cart.clear()
        self.cart_replicator.replicate_cart_clearance(cart.cart_uuid)

        return Response(status=status.HTTP_204_NO_CONTENT)
