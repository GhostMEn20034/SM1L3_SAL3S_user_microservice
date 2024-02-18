from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from unittest import mock

Account = get_user_model()

class MyTestCase(TestCase):

    def test_first_test(self):
        x = 2 + 5
        self.assertEqual(x, 7)


class TestLogin(APITestCase):
    def setUp(self) -> None:

        self.password = "test1234"

        self.user = Account.objects.create_user(
            email="testing44@gmail.com",
            password=self.password,
            first_name="Hello"
        )
        self.inactive_user = Account.objects.create_user(
            email="SomeEmail@gmail.com",
            password=self.password,
            first_name="Hello",
            is_active=False,
        )

    def test_login_with_correct_credentials(self):
        """User that enter correct credentials successfully authenticated"""

        url = reverse('token_obtain_pair')
        # Create a request to the login endpoint
        response = self.client.post(
            url,
            data={
                'email': self.user.email,
                'password': self.password
            },
            format='json'
        )

        # Check that the response status is 200 OK
        self.assertEqual(response.status_code, 200)

    def test_login_with_incorrect_credentials(self):
        """User that enter incorrect credentials fails authentication"""

        url = reverse('token_obtain_pair')
        # Create a request to the login endpoint
        response = self.client.post(
            url,
            data={
                'email': self.user.email,
                'password': 'wrong_password'
            },
            format='json'
        )
        # Check that the response status is 401 UNAUTHORIZED
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @mock.patch('verification.tasks.send_code_signup_confirmation.delay')
    def test_login_as_inactive_user(self, mocked_send_email):
        """User that enter incorrect credentials fails authentication and gets code to the email"""

        url = reverse('token_obtain_pair')

        data = {
            'email': self.inactive_user.email,
            'password': self.password,
        }

        response = self.client.post(url, data=data, format='json')

        # Check that the response status is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that the response data contains a token
        self.assertIn('token', response.data)

        # Check that send_code_signup_confirmation.delay was called once with the user email
        mocked_send_email.assert_called_once_with(data["email"])
