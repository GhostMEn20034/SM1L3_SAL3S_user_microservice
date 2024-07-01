from typing import List
from unittest import mock
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Cart, CartItem
from apps.products.factories import ProductFactory
from apps.products.models import Product
from testing_services.auth_setup import AuthSetupService

Account = get_user_model()


class TestCartRemoving(APITestCase):
    def setUp(self):
        # create multiple product instances
        self.products: List[Product] = [ProductFactory.create() for _ in range(10)]
        # Set up expected max_order_qty and stock to avoid unexpected results.
        # (For example: in the test cart item with qty is added,
        # but product factory set stock to the 1, so test will fail)
        self.products[0].max_order_qty = 6
        self.products[0].stock = 4
        self.products[0].save()

        # The password for users
        self.password = "test1234"
        # Create a user with username and password
        self.first_user = Account.objects.create_user(
            email="testing44@gmail.com",
            password=self.password,
            first_name="Hello",
        )
        # First user's cart
        self.first_users_cart = Cart.objects.create(
            user=self.first_user,
        )

        auth_setup = AuthSetupService(self.client)
        self.access_token = auth_setup.get_auth_token(self.first_user, self.password)

    def test_delete_one_cart_items(self):
        # First user's cart item
        created_cart_item = CartItem.objects.create(
            cart=self.first_users_cart,
            product=self.products[0],
            quantity=1,
        )
        cart_item_id = created_cart_item.product_id

        delete_cart_item_link = reverse('update-or-delete-cart-item',
                                        kwargs={
                                            "cart_uuid": self.first_users_cart.cart_uuid,
                                            "item_id": cart_item_id,
                                        })
        with mock.patch(
                "services.carts.cart_replicator.CartReplicator.replicate_one_cart_item_removal"
        ) as mocked_replication_of_cart_item_delete:
            response = self.client.delete(delete_cart_item_link)
            # Assert that the response status code is 204 (No Content)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            # Assert that replication of cart item delete was called
            self.assertTrue(mocked_replication_of_cart_item_delete.called)

    def test_clear_cart(self):
        # Create cart items
        cart_items = []
        for product in self.products:
            cart_item = CartItem(
                cart=self.first_users_cart,
                product=product,
                quantity=1,
            )
            cart_items.append(cart_item)
        CartItem.objects.bulk_create(cart_items)

        # Assert that cart item's count is equal to the length of the cart_items
        self.assertEqual(self.first_users_cart.count, len(cart_items))

        clear_cart_link = reverse('clear-cart',
                                  kwargs={
                                      "cart_uuid": self.first_users_cart.cart_uuid,
                                  })

        with mock.patch(
                "services.carts.cart_replicator.CartReplicator.replicate_cart_clearance"
        ) as mocked_replication_of_cart_clear:
            response = self.client.post(clear_cart_link)
            # Assert that the response status code is 204 (No Content)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            # Assert that replication of cart clearance was called
            self.assertTrue(mocked_replication_of_cart_clear.called)
