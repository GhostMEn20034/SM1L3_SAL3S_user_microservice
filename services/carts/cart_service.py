from typing import Optional
from uuid import uuid4
from django.db import transaction
from django.db.models import QuerySet
from rest_framework.response import Response
from rest_framework import status

from apps.carts.models import Cart, CartItem
from apps.carts.serialzers import CartSerializer, CartItemSerializer
from .cart_synchronizer import CartSynchronizer


class CartService:
    def __init__(self, cart_queryset, cart_item_queryset):
        self.cart_queryset: QuerySet[Cart] = cart_queryset
        self.cart_item_queryset: QuerySet[CartItem] = cart_item_queryset

    def get_cart_details(self, cart_uuid: uuid4):
        cart: Cart = self.cart_queryset.get(cart_uuid=cart_uuid)
        cart_items = cart.items.select_related('product') \
            .only('quantity', 'product__max_order_qty', 'product__stock',
                  'product__object_id', 'product__name',
                  'product__price', 'product__discount_rate', 'product__image', )
        return cart, cart_items

    def get_by_uuid_or_create_cart(self, cart_uuid: uuid4, user_id: Optional[int]):
        try:
            cart_filters = {}
            if user_id is not None:
                cart_filters['user_id'] = user_id
            else:
                cart_filters['cart_uuid'] = cart_uuid

            cart: Cart = self.cart_queryset.get(**cart_filters)
            cart_serializer = CartSerializer(instance=cart)
            cart_validated_data = cart_serializer.data

            cart_items = [{"product_id": cart_item.product_id, "quantity": cart_item.quantity} for cart_item in
                          CartItem.objects.filter(cart=cart)]

            cart_validated_data["items"] = cart_items
            return cart_validated_data

        except Cart.DoesNotExist:
            cart = Cart.objects.create(user_id=user_id)
            cart.save()

            serializer = CartSerializer(instance=cart)
            cart_data = serializer.data

            cart_data["items"] = []
            return cart_data

    def copy_cart_items(self, user_id, cart_uuid):
        with transaction.atomic():
            try:
                old_cart: Cart = self.cart_queryset.get(cart_uuid=cart_uuid)
                new_cart: Cart = self.cart_queryset.get(user_id=user_id)
            except Cart.DoesNotExist:
                return None

            cart_items: QuerySet[CartItem] = self.cart_item_queryset.filter(cart_id=old_cart.id)
            cloned_cart_items = []
            for cart_item in cart_items:
                cart_item.id = None
                cart_item.cart_id = new_cart.id
                cart_synchronizer = CartSynchronizer(cart_item)
                cart_synchronizer.sync_cart_item_create()
                cloned_cart_items.append(cart_item)

            self.cart_item_queryset.bulk_create(cloned_cart_items)

    def get_cart(self, cart_uuid: uuid4):
        cart, cart_items = self.get_cart_details(cart_uuid)
        cart_serializer = CartSerializer(instance=cart)
        cart_item_serializer = CartItemSerializer(instance=cart_items, many=True)
        return Response(
            data={"cart": cart_serializer.data, "cart_items": cart_item_serializer.data},
            status=status.HTTP_200_OK,
        )

    def create_cart_item(self, cart_uuid: uuid4, data: dict):
        data["cart_id"] = self.cart_queryset.get(cart_uuid=cart_uuid).id
        cart_serializer = CartItemSerializer(data=data)
        if cart_serializer.is_valid():
            created_cart_item = cart_serializer.save()
            cart_synchronizer = CartSynchronizer(created_cart_item)
            cart_synchronizer.sync_cart_item_create()
            return Response(status=status.HTTP_201_CREATED)

        return Response(cart_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update_cart_item(self, cart_uuid: uuid4, item_id: int, data: dict):
        try:
            cart = self.cart_queryset.get(cart_uuid=cart_uuid)
            cart_item: CartItem = self.cart_item_queryset.get(pk=item_id, cart=cart)
        except (CartItem.DoesNotExist, Cart.DoesNotExist):
            return Response({"error": "Cart or its item does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartItemSerializer(instance=cart_item, data=data)
        if serializer.is_valid():
            cart_quantity = serializer.validated_data.get("quantity")
            if cart_quantity > 0:
                cart_item.quantity = serializer.validated_data.get("quantity")

                cart_synchronizer = CartSynchronizer(cart_item=cart_item)
                cart_synchronizer.sync_cart_item_update()
                cart_item.save()
            else:
                cart_synchronizer = CartSynchronizer(cart_item)
                cart_synchronizer.sync_cart_item_delete()
                cart_item.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete_cart_item(self, cart_uuid: uuid4, item_id: int):
        try:
            cart = self.cart_queryset.get(cart_uuid=cart_uuid)
            cart_item: CartItem = self.cart_item_queryset.get(pk=item_id, cart=cart)
        except (CartItem.DoesNotExist, Cart.DoesNotExist):
            return Response({"error": "Cart or its item does not exist"}, status=status.HTTP_404_NOT_FOUND)

        cart_synchronizer = CartSynchronizer(cart_item)
        cart_synchronizer.sync_cart_item_delete()
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def clear_cart(self, cart_uuid: uuid4):
        try:
            cart: Cart = self.cart_queryset.get(cart_uuid=cart_uuid)
        except Cart.DoesNotExist:
            return Response({"error": "Cart does not exist"}, status=status.HTTP_404_NOT_FOUND)

        CartItem.objects.filter(cart=cart).delete()
        cart.total = 0
        cart.count = 0
        cart.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
