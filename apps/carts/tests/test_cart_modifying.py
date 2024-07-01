from typing import List

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest import mock

from apps.products.models import Product
from testing_services.auth_setup import AuthSetupService
from ..models import Cart, CartItem
from apps.products.factories import ProductFactory


Account = get_user_model()


class TestCartModifying(APITestCase):

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

    def test_add_cart_item(self):
        """
        Test adding a cart item to the cart
        """
        create_cart_item_link = reverse('create-cart-item',
                                        kwargs={"cart_uuid": self.first_users_cart.cart_uuid})

        # Set the authorization header with the token
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

        # Add a cart item for the first time
        with mock.patch(
                "services.carts.cart_replicator.CartReplicator.replicate_one_cart_item_creation"
        ) as mocked_replication_of_cart_item_creation:
            response = self.client.post(create_cart_item_link, data={
                "product_id": self.products[0].object_id,
                "quantity": 1,
            }, format='json')
            first_cart_item_id = response.data["cart_item"]["id"]
            # Assert that cart item is created
            self.assertTrue(response.data['created'])
            # Assert that the response status code is 201 (Created)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            # Assert that replication of cart item create was called
            self.assertTrue(mocked_replication_of_cart_item_creation.called)

        # Trying to add the same product to the cart. Expected that it just updates the cart item
        with mock.patch(
                "services.carts.cart_replicator.CartReplicator.replicate_one_cart_item_update"
        ) as mocked_replication_of_cart_item_update:
            response = self.client.post(create_cart_item_link, data={
                "product_id": self.products[0].object_id,
                "quantity": 2,
            }, format='json')
            second_cart_item_id = response.data["cart_item"]["id"]
            # Assert that cart item is created
            self.assertFalse(response.data['created'])
            # Assert that the response status code is 204 (No Content)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            # Assert that replication of cart item create was called
            self.assertTrue(mocked_replication_of_cart_item_update.called)

        # Assert that cart item id from the first and the second responses are the same.
        self.assertEqual(first_cart_item_id, second_cart_item_id)

    def test_update_cart_item(self):
        """
        Test updating a cart item in the cart
        """
        # First user's cart item
        created_cart_item = CartItem.objects.create(
            cart=self.first_users_cart,
            product=self.products[0],
            quantity=1,
        )

        cart_item_id = created_cart_item.product_id

        update_cart_item_link = reverse('update-or-delete-cart-item',
                                        kwargs={
                                            "cart_uuid": self.first_users_cart.cart_uuid,
                                            "item_id": cart_item_id,
                                        })

        # Set the authorization header with the token
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

        with mock.patch(
                "services.carts.cart_replicator.CartReplicator.replicate_one_cart_item_update"
        ) as mocked_replication_of_cart_item_update:
            response = self.client.patch(update_cart_item_link, data={
                "product_id": self.products[0].object_id,
                "quantity": 2,
            }, format='json')
            # Assert that the response status code is 204 (No Content)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            # Assert that replication of cart item update was called
            self.assertTrue(mocked_replication_of_cart_item_update.called)

        updated_cart_item = CartItem.objects.get(product=self.products[0])
        # Assert that cart item's quantity changed to 2
        self.assertEqual(updated_cart_item.quantity, 2)


    def test_delete_cart_item_via_update_route(self):
        """
        When user wants to update the cart item, and he sets quantity to zero, it should delete the cart item.
        """
        # First user's cart item
        created_cart_item = CartItem.objects.create(
            cart=self.first_users_cart,
            product=self.products[0],
            quantity=3,
        )

        cart_item_id = created_cart_item.product_id

        update_cart_item_link = reverse('update-or-delete-cart-item',
                                        kwargs={
                                            "cart_uuid": self.first_users_cart.cart_uuid,
                                            "item_id": cart_item_id,
                                        })
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

        with mock.patch(
                "services.carts.cart_replicator.CartReplicator.replicate_one_cart_item_removal"
        ) as mocked_replication_of_cart_item_delete:
            response = self.client.patch(update_cart_item_link, data={
                "product_id": self.products[0].object_id,
                "quantity": 0,
            }, format='json')
            # Assert that the response status code is 204 (No Content)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            # Assert that replication of cart item delete was called
            self.assertTrue(mocked_replication_of_cart_item_delete.called)

    def test_update_cart_item_with_quantity_gt_max_order_qty(self):
        """
        Trying to set cart item's quantity greater than the max order quantity. Update must be failed
        """
        # Set max_order_qty to 6 for the first product
        self.products[0].max_order_qty = 6
        self.products[0].stock = 18
        self.products[0].save()

        # First user's cart item
        created_cart_item = CartItem.objects.create(
            cart=self.first_users_cart,
            product=self.products[0],
            quantity=4,
        )

        cart_item_id = created_cart_item.product_id

        update_cart_item_link = reverse('update-or-delete-cart-item',
                                        kwargs={
                                            "cart_uuid": self.first_users_cart.cart_uuid,
                                            "item_id": cart_item_id,
                                        })

        response = self.client.patch(update_cart_item_link, data={
            "product_id": self.products[0].object_id,
            "quantity": 7,
        }, format='json')
        # Assert that the response status code is 400 (No Content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


        # Assert that cart item's quantity is still the same
        self.assertEqual(created_cart_item.quantity, 4)

    def test_update_cart_item_with_quantity_gt_stock(self):
        """
        Trying to set cart item's quantity greater than on the stock count. Update must be failed
        """
        # Set stock to 4 for the first product
        self.products[0].max_order_qty = 6
        self.products[0].stock = 4
        self.products[0].save()

        # First user's cart item
        created_cart_item = CartItem.objects.create(
            cart=self.first_users_cart,
            product=self.products[0],
            quantity=2,
        )

        cart_item_id = created_cart_item.product_id

        update_cart_item_link = reverse('update-or-delete-cart-item',
                                        kwargs={
                                            "cart_uuid": self.first_users_cart.cart_uuid,
                                            "item_id": cart_item_id,
                                        })

        response = self.client.patch(update_cart_item_link, data={
            "product_id": self.products[0].object_id,
            "quantity": 5,
        }, format='json')
        # Assert that the response status code is 400 (No Content)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that cart item's quantity is still the same
        self.assertEqual(created_cart_item.quantity, 2)

    def test_add_cart_item_as_anonymous_user(self):
        """
        Test adding a cart item to the cart as the anonymous user
        """
        anonymous_cart = Cart.objects.create(user_id=None)

        create_cart_item_link = reverse('create-cart-item',
                                        kwargs={"cart_uuid": anonymous_cart.cart_uuid})

        # Add a cart item for the first time
        with mock.patch(
                "services.carts.cart_replicator.CartReplicator.replicate_one_cart_item_creation"
        ) as mocked_replication_of_cart_item_creation:
            response = self.client.post(create_cart_item_link, data={
                "product_id": self.products[0].object_id,
                "quantity": 1,
            }, format='json')
            # Assert that cart item is created
            self.assertTrue(response.data['created'])
            # Assert that the response status code is 201 (Created)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            # Assert that replication of cart item create was called
            self.assertTrue(mocked_replication_of_cart_item_creation.called)

    def test_update_cart_item_as_anonymous_user(self):
        """
        Test updating a cart item in the cart as the anonymous user
        """
        # Create the anonymous user's cart
        anonymous_cart = Cart.objects.create(user_id=None)
        # First user's cart item
        created_cart_item = CartItem.objects.create(
            cart=anonymous_cart,
            product=self.products[0],
            quantity=1,
        )

        cart_item_id = created_cart_item.product_id

        update_cart_item_link = reverse('update-or-delete-cart-item',
                                        kwargs={
                                            "cart_uuid": anonymous_cart.cart_uuid,
                                            "item_id": cart_item_id,
                                        })
        with mock.patch(
                "services.carts.cart_replicator.CartReplicator.replicate_one_cart_item_update"
        ) as mocked_replication_of_cart_item_update:
            response = self.client.patch(update_cart_item_link, data={
                "product_id": self.products[0].object_id,
                "quantity": 3,
            }, format='json')
            # Assert that the response status code is 204 (No Content)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            # Assert that replication of cart item update was called
            self.assertTrue(mocked_replication_of_cart_item_update.called)

        updated_cart_item = CartItem.objects.get(product=self.products[0])
        # Assert that cart item's quantity changed to 3
        self.assertEqual(updated_cart_item.quantity, 3)