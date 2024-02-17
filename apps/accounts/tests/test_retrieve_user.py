# Import the necessary modules
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

Account = get_user_model()


class TestRetrieveUser(APITestCase):
    def setUp(self) -> None:
        self.password = "test1234"

        # Create a user with username and password
        self.user = Account.objects.create_user(
            email="testing44@gmail.com",
            password=self.password,
            first_name="Hello"
        )

        # Get the login url
        login_url = reverse("token_obtain_pair")

        # Send the email and password to the login url and get the token
        response = self.client.post(
            login_url,
            data={
                'email': self.user.email,
                'password': self.password
            },
            format='json'
        )

        # Get access token from response
        self.access_token = response.data["access"]

        # Get the user personal info url
        self.user_info_url = reverse("user_personal_info")

    def test_get_user_info_with_correct_token(self):
        """Get user info with correct token"""

        # Set the authorization header with the token
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + self.access_token)

        # Get the user personal info from the url
        response = self.client.get(self.user_info_url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response data contains the user's email
        self.assertEqual(response.data["email"], self.user.email)

    def test_get_user_info_without_token(self):
        """If the user doesn't have an access token, the user will unauthorized"""

        # Get the user personal info from the url
        response = self.client.get(self.user_info_url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        expected_error = {
            "detail": "Authentication credentials were not provided."
        }

        # Assert that the response data contains expected error
        self.assertEqual(response.data, expected_error)
