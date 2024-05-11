from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from apps.products.factories import ProductFactory
from apps.products.models import Product
from .models import RecentlyViewedItem

User = get_user_model()


class HistoryTestCase(APITestCase):
    def setUp(self):
        # create multiple product instances
        self.products = [ProductFactory.create() for _ in range(5)]
        product_length = len(self.products)

        # create a user
        users_password = 'test1488'
        self.user = User.objects.create_user(
            email='test1488@gmail.com',
            password=users_password,
            first_name='NiceMan1488',
        )

        self.another_user = User.objects.create_user(
            email='test4444@gmail.com',
            password=users_password,
            first_name='GhostMe4444',
        )

        self.recently_viewed_items = [
            RecentlyViewedItem.objects.create(
                product=self.products[i],
                user=self.user,
            ) for i in range(product_length)
        ]

        # Get the login url
        login_url = reverse("token_obtain_pair")
        # Send the email and password to the login url and get the token
        user_credentials = self.client.post(
            login_url,
            data={
                'email': self.user.email,
                'password': users_password,
            },
            format='json'
        )

        # Login another user
        another_user_credentials = self.client.post(
            login_url,
            data={
                'email': self.another_user.email,
                'password': users_password,
            },
            format='json'
        )

        # Get access token from response
        self.access_token = user_credentials.data["access"]
        # Get access token for another user
        self.another_access_token = another_user_credentials.data["access"]

    def test_retrieve_list_of_recently_viewed_items(self):
        """
        Test retrieval of recently viewed items as authenticated user.
        """
        # Set the authorization header with the token
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

        history_list_url = reverse('history-list')
        response = self.client.get(history_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 5)

    def test_retrieve_recently_viewed_items_unauthorized(self):
        """
        Test retrieval of recently viewed items as unauthenticated user.
        """
        history_list_url = reverse('history-list')
        response = self.client.get(history_list_url)
        # Assert that the response status code is 401 (Unauthorized)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_view_someones_else_recently_viewed_items(self):
        """
        Ensures that other users can't view someone's else recently viewed items.
        """
        # Set the authorization header with the token
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.another_access_token)

        history_list_url = reverse('history-list')
        response = self.client.get(history_list_url)
        # Since recently viewed items were not created for another user, expected 0 items in result
        self.assertEqual(len(response.data.get("results")), 0)

    def test_recently_viewed_item_create(self):
        """
        Ensures that recently viewed item is created properly in history-list route.
        """
        # Set the authorization header with the token
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.another_access_token)

        history_list_url = reverse('history-list')

        response = self.client.post(history_list_url, data={
            'product': self.products[0].object_id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("view_count"), 1)

    def test_recently_viewed_item_update(self):
        """
        Ensures that recently viewed item is updated properly in history-list route.
        """
        # Set the authorization header with the token
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

        history_list_url = reverse('history-list')

        response = self.client.post(history_list_url, data={
            'product': self.products[0].object_id,
        }, format='json')
        updated_recently_viewed_item = RecentlyViewedItem.objects.get(product_id=self.products[0].object_id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(updated_recently_viewed_item.view_count, 2)

    def test_recently_viewed_item_delete(self):
        """
        Ensures that recently viewed item is deleted properly.
        """
        # Set the authorization header with the token
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

        initial_length_of_recently_viewed_items = len(self.recently_viewed_items)

        history_detail_url = reverse('history-detail',
                                     kwargs={'pk': self.recently_viewed_items[0].id})
        response = self.client.delete(history_detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RecentlyViewedItem.objects.all().count(), initial_length_of_recently_viewed_items - 1)

    def test_recently_viewed_item_delete_all(self):
        """
        Ensures that all recently viewed items are deleted properly.
        """
        # Set the authorization header with the token
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

        history_destroy_all_url = reverse('history-destroy-all')

        response = self.client.delete(history_destroy_all_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RecentlyViewedItem.objects.all().count(), 0)
